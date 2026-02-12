from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import MachineStatus, UserRole
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineKPI, MachineUpdate


def _days_between(start: date | None, end: date | None) -> int | None:
    if not start or not end:
        return None
    return (end - start).days


def validate_machine_dates(machine: Machine) -> None:
    """Validate chronological order and status-dependent date requirements."""

    if machine.status == MachineStatus.INTAKE_ASSESSMENT and machine.dt_arrival_refurb is None:
        raise HTTPException(status_code=400, detail='INTAKE_ASSESSMENT requires dt_arrival_refurb')
    if machine.status == MachineStatus.REFURBISHMENT and machine.dt_workshop_start is None:
        raise HTTPException(status_code=400, detail='REFURBISHMENT requires dt_workshop_start')
    if machine.status == MachineStatus.SALE_READY and machine.dt_sale_ready is None:
        raise HTTPException(status_code=400, detail='SALE_READY requires dt_sale_ready')

    checkpoints = [
        ('dt_rental_exit', machine.dt_rental_exit),
        ('dt_arrival_refurb', machine.dt_arrival_refurb),
        ('dt_workshop_start', machine.dt_workshop_start),
        ('dt_tech_done', machine.dt_tech_done),
        ('dt_sale_ready', machine.dt_sale_ready),
    ]
    previous_name = None
    previous_value = None
    for name, value in checkpoints:
        if value is None:
            continue
        if previous_value and value < previous_value:
            raise HTTPException(
                status_code=400,
                detail=f'Date logic invalid: {name} ({value}) cannot be before {previous_name} ({previous_value})',
            )
        previous_name = name
        previous_value = value


def compute_kpi(machine: Machine, today: date | None = None) -> MachineKPI:
    today = today or date.today()
    transport_days = _days_between(machine.dt_rental_exit, machine.dt_arrival_refurb)
    intake_days = _days_between(machine.dt_arrival_refurb, machine.dt_workshop_start)
    refurb_days = _days_between(machine.dt_workshop_start, machine.dt_sale_ready or machine.dt_tech_done)
    total_days = _days_between(machine.dt_rental_exit, machine.dt_sale_ready)

    status_start = {
        MachineStatus.UNDERWAY: machine.dt_rental_exit,
        MachineStatus.INTAKE_ASSESSMENT: machine.dt_arrival_refurb,
        MachineStatus.REFURBISHMENT: machine.dt_workshop_start,
        MachineStatus.SALE_READY: machine.dt_sale_ready,
    }.get(machine.status) or machine.dt_rental_exit
    days_in_current_status = max((today - status_start).days, 0)

    capital_binding = None
    if machine.estimated_market_value_eur is not None and total_days is not None:
        capital_binding = (Decimal(machine.estimated_market_value_eur) * Decimal(total_days) / Decimal(365)).quantize(
            Decimal('0.01')
        )

    return MachineKPI(
        machine_id=machine.id,
        transport_days=transport_days,
        intake_days=intake_days,
        refurb_days=refurb_days,
        total_days_to_sale_ready=total_days,
        days_in_current_status=days_in_current_status,
        capital_binding=capital_binding,
    )


def list_machines(db: Session, site: str | None, status: str | None, older_than_days: int | None) -> list[Machine]:
    query = select(Machine)
    if site:
        query = query.where(Machine.refurb_site == site)
    if status:
        query = query.where(Machine.status == status)
    machines = db.scalars(query.order_by(Machine.created_at.desc())).all()
    if older_than_days is not None:
        return [m for m in machines if compute_kpi(m).days_in_current_status > older_than_days]
    return machines


def create_machine(db: Session, payload: MachineCreate) -> Machine:
    existing = db.scalar(select(Machine).where(Machine.machine_number == payload.machine_number))
    if existing:
        raise HTTPException(status_code=400, detail='machine_number must be unique')
    machine = Machine(**payload.model_dump())
    validate_machine_dates(machine)
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


def update_machine(db: Session, machine: Machine, payload: MachineUpdate, role: str, user_site: str | None) -> Machine:
    if role == UserRole.SITE_USER.value and user_site != machine.refurb_site.value:
        raise HTTPException(status_code=403, detail='SiteUser can only update machines of own refurb_site')

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(machine, key, value)

    validate_machine_dates(machine)
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


def get_overview(db: Session) -> dict:
    machines = db.scalars(select(Machine)).all()
    status_counts = {status.value: 0 for status in MachineStatus}
    for m in machines:
        status_counts[m.status.value] += 1

    by_site: dict[str, list[Machine]] = {}
    for m in machines:
        by_site.setdefault(m.refurb_site.value, []).append(m)

    avg_total_days_by_site: dict[str, float] = {}
    capital_binding_by_site: dict[str, Decimal] = {}
    all_kpi = [compute_kpi(m) for m in machines]
    for site, site_machines in by_site.items():
        totals = [k.total_days_to_sale_ready for k in (compute_kpi(m) for m in site_machines) if k.total_days_to_sale_ready is not None]
        avg_total_days_by_site[site] = round(sum(totals) / len(totals), 2) if totals else 0.0
        capital_binding_by_site[site] = sum((compute_kpi(m).capital_binding or Decimal('0.00')) for m in site_machines)

    return {
        'status_counts': status_counts,
        'avg_total_days_by_site': avg_total_days_by_site,
        'aging_over_30': len([k for k in all_kpi if k.days_in_current_status > 30]),
        'aging_over_45': len([k for k in all_kpi if k.days_in_current_status > 45]),
        'capital_binding_by_site': capital_binding_by_site,
    }


def get_site_comparison(db: Session) -> list[dict]:
    machines = db.scalars(select(Machine)).all()
    grouped: dict[str, list[Machine]] = {}
    for m in machines:
        grouped.setdefault(m.refurb_site.value, []).append(m)

    result = []
    for site, items in grouped.items():
        kpis = [compute_kpi(m) for m in items]
        totals = [k.total_days_to_sale_ready for k in kpis if k.total_days_to_sale_ready is not None]
        result.append(
            {
                'site': site,
                'machine_count': len(items),
                'avg_total_days': round(sum(totals) / len(totals), 2) if totals else 0.0,
                'capital_binding': sum((k.capital_binding or Decimal('0.00')) for k in kpis),
            }
        )
    return sorted(result, key=lambda x: x['site'])


def get_slowest(db: Session) -> list[dict]:
    machines = db.scalars(select(Machine)).all()
    data = []
    for m in machines:
        kpi = compute_kpi(m)
        data.append(
            {
                'machine_number': m.machine_number,
                'refurb_site': m.refurb_site.value,
                'status': m.status.value,
                'days_in_current_status': kpi.days_in_current_status,
                'total_days_to_sale_ready': kpi.total_days_to_sale_ready,
            }
        )
    return sorted(data, key=lambda x: x['days_in_current_status'], reverse=True)[:10]

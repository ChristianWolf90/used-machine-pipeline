from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import MachineStatus, UserRole
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineKPI, MachineUpdate


def _days_between(start: date | None, end: date | None) -> int | None:
    if not start or not end:
        return None
    return (end - start).days


def get_total_process_days(machine: Machine, today: date | None = None) -> int:
    today = today or date.today()
    process_end = machine.dt_sale_ready or today
    return max((process_end - machine.dt_rental_exit).days, 0)


def get_traffic_light(total_process_days: int) -> str:
    # Ampellogik für Gesamtverweildauer im Prozess.
    if total_process_days < 30:
        return 'GREEN'
    if total_process_days <= 45:
        return 'YELLOW'
    return 'RED'


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


def to_machine_response(machine: Machine, today: date | None = None) -> dict:
    total_process_days = get_total_process_days(machine, today)
    return {
        'id': machine.id,
        'machine_number': machine.machine_number,
        'type_model': machine.type_model,
        'value_class': machine.value_class,
        'estimated_market_value_eur': machine.estimated_market_value_eur,
        'rental_origin_site': machine.rental_origin_site,
        'refurb_site': machine.refurb_site,
        'status': machine.status,
        'dt_rental_exit': machine.dt_rental_exit,
        'dt_arrival_refurb': machine.dt_arrival_refurb,
        'dt_workshop_start': machine.dt_workshop_start,
        'dt_tech_done': machine.dt_tech_done,
        'dt_sale_ready': machine.dt_sale_ready,
        'notes': machine.notes,
        'created_at': machine.created_at,
        'updated_at': machine.updated_at,
        'total_process_days': total_process_days,
        'traffic_light': get_traffic_light(total_process_days),
    }


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


def _safe_avg(values: list[int]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def get_dashboard_operations(db: Session) -> dict:
    machines = db.scalars(select(Machine)).all()
    today = date.today()

    total_days = [get_total_process_days(machine, today) for machine in machines]
    arrival_days = [max((today - machine.dt_arrival_refurb).days, 0) for machine in machines if machine.dt_arrival_refurb]

    transport_machines = [machine for machine in machines if machine.status == MachineStatus.UNDERWAY]
    intake_machines = [machine for machine in machines if machine.status == MachineStatus.INTAKE_ASSESSMENT]
    workshop_machines = [machine for machine in machines if machine.status == MachineStatus.REFURBISHMENT]

    transport_durations = [
        max((today - machine.dt_rental_exit).days, 0) if machine.dt_arrival_refurb is None else max((machine.dt_arrival_refurb - machine.dt_rental_exit).days, 0)
        for machine in machines
        if machine.status == MachineStatus.UNDERWAY or machine.dt_arrival_refurb is not None
    ]
    intake_durations = [
        max((today - machine.dt_arrival_refurb).days, 0) if machine.dt_workshop_start is None else max((machine.dt_workshop_start - machine.dt_arrival_refurb).days, 0)
        for machine in machines
        if machine.status == MachineStatus.INTAKE_ASSESSMENT or (machine.dt_arrival_refurb and machine.dt_workshop_start)
    ]
    workshop_durations = [
        max((today - machine.dt_workshop_start).days, 0)
        if machine.dt_sale_ready is None and machine.dt_tech_done is None
        else max(((machine.dt_sale_ready or machine.dt_tech_done) - machine.dt_workshop_start).days, 0)
        for machine in machines
        if machine.status == MachineStatus.REFURBISHMENT or machine.dt_workshop_start is not None
    ]

    oldest_transports = sorted(
        (
            {
                'machine_id': str(machine.id),
                'machine_number': machine.machine_number,
                'refurb_site': machine.refurb_site.value,
                'transport_days': max((today - machine.dt_rental_exit).days, 0),
                'total_process_days': get_total_process_days(machine, today),
                'traffic_light': get_traffic_light(get_total_process_days(machine, today)),
            }
            for machine in transport_machines
        ),
        key=lambda item: item['transport_days'],
        reverse=True,
    )[:5]

    intake_highlights = []
    for machine in intake_machines:
        stage_days = max((today - machine.dt_arrival_refurb).days, 0) if machine.dt_arrival_refurb else 0
        intake_highlights.append(
            {
                'machine_id': str(machine.id),
                'machine_number': machine.machine_number,
                'refurb_site': machine.refurb_site.value,
                'status': machine.status.value,
                'stage_days': stage_days,
                'total_process_days': get_total_process_days(machine, today),
                'estimated_market_value_eur': float(machine.estimated_market_value_eur) if machine.estimated_market_value_eur else None,
                'traffic_light': get_traffic_light(get_total_process_days(machine, today)),
            }
        )

    workshop_highlights = []
    for machine in workshop_machines:
        stage_days = max((today - machine.dt_workshop_start).days, 0) if machine.dt_workshop_start else 0
        workshop_highlights.append(
            {
                'machine_id': str(machine.id),
                'machine_number': machine.machine_number,
                'refurb_site': machine.refurb_site.value,
                'status': machine.status.value,
                'stage_days': stage_days,
                'total_process_days': get_total_process_days(machine, today),
                'estimated_market_value_eur': float(machine.estimated_market_value_eur) if machine.estimated_market_value_eur else None,
                'traffic_light': get_traffic_light(get_total_process_days(machine, today)),
            }
        )

    return {
        'top_kpis': {
            'total_machines_in_process': len(machines),
            'average_days_since_arrival': _safe_avg(arrival_days),
            'machines_over_30_days': len([days for days in total_days if days > 30]),
            'machines_over_45_days': len([days for days in total_days if days > 45]),
        },
        'transport': {
            'average_transport_days': _safe_avg(transport_durations),
            'underway_count': len(transport_machines),
            'oldest_transports': oldest_transports,
        },
        'intake_assessment': {
            'average_arrival_to_workshop_days': _safe_avg(intake_durations),
            'intake_assessment_count': len(intake_machines),
            'highlighted_machines': sorted(intake_highlights, key=lambda item: item['stage_days'], reverse=True),
        },
        'workshop': {
            'average_workshop_to_done_days': _safe_avg(workshop_durations),
            'refurbishment_count': len(workshop_machines),
            'highlighted_machines': sorted(workshop_highlights, key=lambda item: item['stage_days'], reverse=True),
        },
    }


def get_site_worklist(db: Session, site: str | None, status: str | None) -> list[dict]:
    machines = db.scalars(select(Machine)).all()
    today = date.today()

    filtered = []
    for machine in machines:
        if site and machine.refurb_site.value != site:
            continue
        if status and machine.status.value != status:
            continue
        total_days = get_total_process_days(machine, today)
        filtered.append(
            {
                'machine_id': str(machine.id),
                'machine_number': machine.machine_number,
                'refurb_site': machine.refurb_site.value,
                'status': machine.status.value,
                'total_process_days': total_days,
                'estimated_market_value_eur': float(machine.estimated_market_value_eur) if machine.estimated_market_value_eur else None,
                'traffic_light': get_traffic_light(total_days),
            }
        )

    # Priorisierung für die Standort-Arbeitsliste: Rot, Gelb, Grün.
    light_priority = {'RED': 0, 'YELLOW': 1, 'GREEN': 2}
    return sorted(
        filtered,
        key=lambda item: (
            light_priority.get(item['traffic_light'], 3),
            -((item['estimated_market_value_eur']) or 0),
            -item['total_process_days'],
        ),
    )

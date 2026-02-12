"""Seed script for demo users and machines."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.enums import MachineStatus, RefurbSite, UserRole, ValueClass
from app.models.machine import Machine
from app.models.user import User


def seed_users(db):
    users = [
        ('admin', 'admin123', UserRole.ADMIN, None),
        ('passau_user', 'site123', UserRole.SITE_USER, RefurbSite.PASSAU),
        ('andernach_user', 'site123', UserRole.SITE_USER, RefurbSite.ANDERNACH),
        ('welzow_user', 'site123', UserRole.SITE_USER, RefurbSite.WELZOW),
    ]
    for username, password, role, site in users:
        existing = db.scalar(select(User).where(User.username == username))
        if not existing:
            db.add(User(username=username, password_hash=get_password_hash(password), role=role, site=site))


def seed_machines(db):
    if db.scalar(select(Machine)):
        return

    today = date.today()
    machines = [
        Machine(
            machine_number='UM-1001',
            type_model='CAT 320',
            value_class=ValueClass.A,
            estimated_market_value_eur=Decimal('120000.00'),
            rental_origin_site='München',
            refurb_site=RefurbSite.PASSAU,
            status=MachineStatus.REFURBISHMENT,
            dt_rental_exit=today - timedelta(days=40),
            dt_arrival_refurb=today - timedelta(days=35),
            dt_workshop_start=today - timedelta(days=30),
            notes='Hydraulik prüfen',
        ),
        Machine(
            machine_number='UM-1002',
            type_model='Liebherr LTM',
            value_class=ValueClass.B,
            estimated_market_value_eur=Decimal('80000.00'),
            rental_origin_site='Nürnberg',
            refurb_site=RefurbSite.ANDERNACH,
            status=MachineStatus.INTAKE_ASSESSMENT,
            dt_rental_exit=today - timedelta(days=20),
            dt_arrival_refurb=today - timedelta(days=15),
        ),
        Machine(
            machine_number='UM-1003',
            type_model='Volvo EC250',
            value_class=ValueClass.C,
            estimated_market_value_eur=Decimal('60000.00'),
            rental_origin_site='Leipzig',
            refurb_site=RefurbSite.WELZOW,
            status=MachineStatus.SALE_READY,
            dt_rental_exit=today - timedelta(days=55),
            dt_arrival_refurb=today - timedelta(days=50),
            dt_workshop_start=today - timedelta(days=47),
            dt_tech_done=today - timedelta(days=10),
            dt_sale_ready=today - timedelta(days=5),
        ),
    ]
    db.add_all(machines)


def main() -> None:
    db = SessionLocal()
    try:
        seed_users(db)
        seed_machines(db)
        db.commit()
        print('Seed completed.')
    finally:
        db.close()


if __name__ == '__main__':
    main()

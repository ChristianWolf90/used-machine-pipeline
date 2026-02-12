"""init schema

Revision ID: 202610010001
Revises:
Create Date: 2026-10-01 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '202610010001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


machine_status_enum = sa.Enum('UNDERWAY', 'INTAKE_ASSESSMENT', 'REFURBISHMENT', 'SALE_READY', name='machine_status_enum')
value_class_enum = sa.Enum('A', 'B', 'C', name='value_class_enum')
refurb_site_enum = sa.Enum('Passau', 'Andernach', 'Welzow', name='refurb_site_enum')
user_role_enum = sa.Enum('Admin', 'SiteUser', name='user_role_enum')


def upgrade() -> None:
    machine_status_enum.create(op.get_bind(), checkfirst=True)
    value_class_enum.create(op.get_bind(), checkfirst=True)
    refurb_site_enum.create(op.get_bind(), checkfirst=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'machines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('machine_number', sa.String(length=50), nullable=False),
        sa.Column('type_model', sa.String(length=120), nullable=True),
        sa.Column('value_class', value_class_enum, nullable=True),
        sa.Column('estimated_market_value_eur', sa.Numeric(14, 2), nullable=True),
        sa.Column('rental_origin_site', sa.String(length=120), nullable=True),
        sa.Column('refurb_site', refurb_site_enum, nullable=False),
        sa.Column('status', machine_status_enum, nullable=False),
        sa.Column('dt_rental_exit', sa.Date(), nullable=False),
        sa.Column('dt_arrival_refurb', sa.Date(), nullable=True),
        sa.Column('dt_workshop_start', sa.Date(), nullable=True),
        sa.Column('dt_tech_done', sa.Date(), nullable=True),
        sa.Column('dt_sale_ready', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_machines_machine_number'), 'machines', ['machine_number'], unique=True)

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('site', refurb_site_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_machines_machine_number'), table_name='machines')
    op.drop_table('machines')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
    refurb_site_enum.drop(op.get_bind(), checkfirst=True)
    value_class_enum.drop(op.get_bind(), checkfirst=True)
    machine_status_enum.drop(op.get_bind(), checkfirst=True)

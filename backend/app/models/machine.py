import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import MachineStatus, RefurbSite, ValueClass


class Machine(Base):
    __tablename__ = 'machines'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    type_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    value_class: Mapped[ValueClass | None] = mapped_column(Enum(ValueClass, name='value_class_enum'), nullable=True)
    estimated_market_value_eur: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    rental_origin_site: Mapped[str | None] = mapped_column(String(120), nullable=True)
    refurb_site: Mapped[RefurbSite] = mapped_column(Enum(RefurbSite, name='refurb_site_enum'), nullable=False)
    status: Mapped[MachineStatus] = mapped_column(
        Enum(MachineStatus, name='machine_status_enum'), nullable=False, default=MachineStatus.UNDERWAY
    )

    dt_rental_exit: Mapped[date] = mapped_column(Date, nullable=False)
    dt_arrival_refurb: Mapped[date | None] = mapped_column(Date, nullable=True)
    dt_workshop_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    dt_tech_done: Mapped[date | None] = mapped_column(Date, nullable=True)
    dt_sale_ready: Mapped[date | None] = mapped_column(Date, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

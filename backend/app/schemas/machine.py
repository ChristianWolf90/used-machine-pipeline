import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import MachineStatus, RefurbSite, ValueClass


class MachineBase(BaseModel):
    machine_number: str
    type_model: str | None = None
    value_class: ValueClass | None = None
    estimated_market_value_eur: Decimal | None = None
    rental_origin_site: str | None = None
    refurb_site: RefurbSite
    status: MachineStatus = MachineStatus.UNDERWAY
    dt_rental_exit: date
    dt_arrival_refurb: date | None = None
    dt_workshop_start: date | None = None
    dt_tech_done: date | None = None
    dt_sale_ready: date | None = None
    notes: str | None = None


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    type_model: str | None = None
    value_class: ValueClass | None = None
    estimated_market_value_eur: Decimal | None = None
    rental_origin_site: str | None = None
    refurb_site: RefurbSite | None = None
    status: MachineStatus | None = None
    dt_rental_exit: date | None = None
    dt_arrival_refurb: date | None = None
    dt_workshop_start: date | None = None
    dt_tech_done: date | None = None
    dt_sale_ready: date | None = None
    notes: str | None = None


class MachineResponse(MachineBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    total_process_days: int
    traffic_light: str

    class Config:
        from_attributes = True


class MachineKPI(BaseModel):
    machine_id: uuid.UUID
    transport_days: int | None
    intake_days: int | None
    refurb_days: int | None
    total_days_to_sale_ready: int | None
    days_in_current_status: int
    capital_binding: Decimal | None = Field(default=None)

from decimal import Decimal

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    status_counts: dict[str, int]
    avg_total_days_by_site: dict[str, float]
    aging_over_30: int
    aging_over_45: int
    capital_binding_by_site: dict[str, Decimal]


class SiteComparisonItem(BaseModel):
    site: str
    machine_count: int
    avg_total_days: float
    capital_binding: Decimal


class SlowestMachineItem(BaseModel):
    machine_number: str
    refurb_site: str
    status: str
    days_in_current_status: int
    total_days_to_sale_ready: int | None

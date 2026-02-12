from pydantic import BaseModel


class TopKpiResponse(BaseModel):
    total_machines_in_process: int
    average_days_since_arrival: float
    machines_over_30_days: int
    machines_over_45_days: int


class TransportOldestItem(BaseModel):
    machine_id: str
    machine_number: str
    refurb_site: str
    transport_days: int
    total_process_days: int
    traffic_light: str


class AgingMachineItem(BaseModel):
    machine_id: str
    machine_number: str
    refurb_site: str
    status: str
    stage_days: int
    total_process_days: int
    estimated_market_value_eur: float | None
    traffic_light: str


class TransportBlockResponse(BaseModel):
    average_transport_days: float
    underway_count: int
    oldest_transports: list[TransportOldestItem]


class IntakeAssessmentBlockResponse(BaseModel):
    average_arrival_to_workshop_days: float
    intake_assessment_count: int
    highlighted_machines: list[AgingMachineItem]


class WorkshopBlockResponse(BaseModel):
    average_workshop_to_done_days: float
    refurbishment_count: int
    highlighted_machines: list[AgingMachineItem]


class DashboardOperationsResponse(BaseModel):
    top_kpis: TopKpiResponse
    transport: TransportBlockResponse
    intake_assessment: IntakeAssessmentBlockResponse
    workshop: WorkshopBlockResponse


class SiteWorklistItem(BaseModel):
    machine_id: str
    machine_number: str
    refurb_site: str
    status: str
    total_process_days: int
    estimated_market_value_eur: float | None
    traffic_light: str


class SiteWorklistResponse(BaseModel):
    items: list[SiteWorklistItem]

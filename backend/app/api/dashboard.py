from fastapi import APIRouter

from app.core.deps import DbDep, UserDep
from app.schemas.dashboard import OverviewResponse, SiteComparisonItem, SlowestMachineItem
from app.services.machine_service import get_overview, get_site_comparison, get_slowest

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/overview', response_model=OverviewResponse)
def overview(db: DbDep, _: UserDep) -> OverviewResponse:
    return OverviewResponse(**get_overview(db))


@router.get('/site-comparison', response_model=list[SiteComparisonItem])
def site_comparison(db: DbDep, _: UserDep) -> list[SiteComparisonItem]:
    return [SiteComparisonItem(**item) for item in get_site_comparison(db)]


@router.get('/slowest', response_model=list[SlowestMachineItem])
def slowest(db: DbDep, _: UserDep) -> list[SlowestMachineItem]:
    return [SlowestMachineItem(**item) for item in get_slowest(db)]

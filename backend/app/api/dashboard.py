from fastapi import APIRouter, Query

from app.core.deps import DbDep, UserDep
from app.schemas.dashboard import DashboardOperationsResponse, SiteWorklistResponse
from app.services.machine_service import get_dashboard_operations, get_site_worklist

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/operations', response_model=DashboardOperationsResponse)
def operations(db: DbDep, _: UserDep) -> DashboardOperationsResponse:
    return DashboardOperationsResponse(**get_dashboard_operations(db))


@router.get('/site-worklist', response_model=SiteWorklistResponse)
def site_worklist(
    db: DbDep,
    _: UserDep,
    site: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> SiteWorklistResponse:
    return SiteWorklistResponse(items=get_site_worklist(db, site=site, status=status))

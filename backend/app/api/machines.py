import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.deps import DbDep, UserDep
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineResponse, MachineUpdate
from app.services.machine_service import create_machine, list_machines, to_machine_response, update_machine

router = APIRouter(prefix='/machines', tags=['machines'])


@router.get('', response_model=list[MachineResponse])
def get_machines(
    db: DbDep,
    _: UserDep,
    site: str | None = Query(default=None),
    status: str | None = Query(default=None),
    older_than_days: int | None = Query(default=None),
) -> list[MachineResponse]:
    machines = list_machines(db, site=site, status=status, older_than_days=older_than_days)
    return [MachineResponse(**to_machine_response(machine)) for machine in machines]


@router.post('', response_model=MachineResponse)
def post_machine(payload: MachineCreate, db: DbDep, user: UserDep) -> MachineResponse:
    if user.role not in ('Admin', 'SiteUser'):
        raise HTTPException(status_code=403, detail='Not allowed')
    return MachineResponse(**to_machine_response(create_machine(db, payload)))


@router.put('/{machine_id}', response_model=MachineResponse)
def put_machine(machine_id: uuid.UUID, payload: MachineUpdate, db: DbDep, user: UserDep) -> MachineResponse:
    machine = db.scalar(select(Machine).where(Machine.id == machine_id))
    if not machine:
        raise HTTPException(status_code=404, detail='Machine not found')
    return MachineResponse(**to_machine_response(update_machine(db, machine, payload, role=user.role, user_site=user.site)))

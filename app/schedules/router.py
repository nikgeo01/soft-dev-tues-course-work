from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.dependencies import get_db, require_doctor
from app.schedules.schemas import (
    PermanentChangeRequest,
    PermanentChangeResponse,
    TemporaryOverrideRequest,
    TemporaryOverrideResponse,
    TimeSlotResponse,
    WeeklyScheduleResponse,
    WorkingHoursUpdateRequest,
)
from app.schedules.service import (
    create_permanent_change,
    create_temporary_override,
    delete_temporary_override,
    get_effective_schedule,
    update_working_hours,
)

router = APIRouter(prefix="/doctors", tags=["schedules"])


@router.put("/me/schedule", response_model=WeeklyScheduleResponse)
async def update_my_schedule(
    body: WorkingHoursUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_doctor)],
) -> WeeklyScheduleResponse:
    return await update_working_hours(db, user.id, body)


@router.get("/{doctor_id}/schedule", response_model=list[TimeSlotResponse])
async def get_doctor_schedule(
    doctor_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    schedule_date: Annotated[
        date,
        Query(alias="date", default_factory=date.today),
    ],
) -> list[TimeSlotResponse]:
    return await get_effective_schedule(db, doctor_id, schedule_date)


@router.post(
    "/me/schedule/temporary",
    response_model=TemporaryOverrideResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_temporary_override(
    body: TemporaryOverrideRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_doctor)],
) -> TemporaryOverrideResponse:
    return await create_temporary_override(db, user.id, body)


@router.delete("/me/schedule/temporary", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_temporary_override(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_doctor)],
) -> Response:
    await delete_temporary_override(db, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/me/schedule/permanent",
    response_model=PermanentChangeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_permanent_change(
    body: PermanentChangeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_doctor)],
) -> PermanentChangeResponse:
    return await create_permanent_change(db, user.id, body)

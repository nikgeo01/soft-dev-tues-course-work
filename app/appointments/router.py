from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.schemas import (
    AppointmentCreateRequest,
    AppointmentListFilters,
    AppointmentListResponse,
    AppointmentResponse,
)
from app.appointments.service import (
    cancel_appointment,
    create_appointment,
    list_appointments,
)
from app.auth.models import User
from app.dependencies import get_current_user, get_db, require_patient

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment_endpoint(
    body: AppointmentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_patient)],
) -> AppointmentResponse:
    return await create_appointment(db, user.id, body)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment_endpoint(
    appointment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    await cancel_appointment(db, user, appointment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=AppointmentListResponse)
async def list_appointments_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: Optional[date] = None,  # noqa: UP045
    date_to: Optional[date] = None,  # noqa: UP045
    appointment_status: Annotated[Optional[str], Query(alias="status")] = None,  # noqa: UP045
) -> AppointmentListResponse:
    filters = AppointmentListFilters(
        date_from=date_from,
        date_to=date_to,
        status=appointment_status,
    )
    return await list_appointments(
        db=db,
        user=user,
        filters=filters,
        skip=skip,
        limit=limit,
    )

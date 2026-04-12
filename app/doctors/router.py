from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.doctors.schemas import DoctorListResponse, DoctorResponse
from app.doctors.service import get_doctor, list_doctors

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=DoctorListResponse)
async def list_doctors_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> DoctorListResponse:
    return await list_doctors(db, skip=skip, limit=limit)


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor_endpoint(
    doctor_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DoctorResponse:
    return await get_doctor(db, doctor_id)

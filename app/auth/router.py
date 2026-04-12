from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    DoctorRegisterRequest,
    LoginRequest,
    PatientRegisterRequest,
    TokenResponse,
)
from app.auth.service import authenticate, register_doctor, register_patient
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register/doctor",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_doctor_endpoint(
    body: DoctorRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await register_doctor(db, body)


@router.post(
    "/register/patient",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_patient_endpoint(
    body: PatientRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await register_patient(db, body)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await authenticate(db, body)

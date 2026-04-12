from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import (
    DoctorRegisterRequest,
    LoginRequest,
    PatientRegisterRequest,
    TokenResponse,
)
from app.auth.security import create_access_token, hash_password, verify_password
from app.common.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.doctors.models import Doctor
from app.patients.models import Patient
from app.schedules.models import WorkingHours


async def register_doctor(
    db: AsyncSession,
    data: DoctorRegisterRequest,
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none() is not None:
        raise ConflictException(
            code="EMAIL_EXISTS",
            message="An account with this email already exists.",
        )

    hashed = hash_password(data.password)
    user = User(email=data.email, hashed_password=hashed, role="doctor")
    db.add(user)
    await db.flush()

    doctor = Doctor(id=user.id, name=data.name, address=data.address)
    db.add(doctor)

    for slot in data.working_hours:
        db.add(
            WorkingHours(
                doctor_id=user.id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                is_break=slot.is_break,
            )
        )

    await db.commit()
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)


async def register_patient(
    db: AsyncSession,
    data: PatientRegisterRequest,
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none() is not None:
        raise ConflictException(
            code="EMAIL_EXISTS",
            message="An account with this email already exists.",
        )

    doctor_result = await db.execute(select(Doctor).where(Doctor.id == data.doctor_id))
    if doctor_result.scalar_one_or_none() is None:
        raise NotFoundException(
            code="DOCTOR_NOT_FOUND",
            message="No doctor found with the given id.",
        )

    hashed = hash_password(data.password)
    user = User(email=data.email, hashed_password=hashed, role="patient")
    db.add(user)
    await db.flush()

    patient = Patient(
        id=user.id,
        name=data.name,
        phone=data.phone,
        doctor_id=data.doctor_id,
    )
    db.add(patient)
    await db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)


async def authenticate(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedException(
            code="INVALID_CREDENTIALS",
            message="Incorrect email or password.",
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.exceptions import NotFoundException
from app.doctors.models import Doctor
from app.doctors.schemas import DoctorListResponse, DoctorResponse, WorkingHoursResponse


def _sorted_working_hours(doctor: Doctor) -> list[WorkingHoursResponse]:
    hours = sorted(
        doctor.working_hours,
        key=lambda wh: (wh.day_of_week, wh.start_time),
    )
    return [WorkingHoursResponse.model_validate(wh) for wh in hours]


def _doctor_to_response(doctor: Doctor) -> DoctorResponse:
    return DoctorResponse(
        id=doctor.id,
        name=doctor.name,
        email=doctor.user.email,
        address=doctor.address,
        working_hours=_sorted_working_hours(doctor),
    )


async def list_doctors(
    db: AsyncSession,
    skip: int,
    limit: int,
) -> DoctorListResponse:
    total_result = await db.execute(select(func.count()).select_from(Doctor))
    total = int(total_result.scalar_one())

    stmt = (
        select(Doctor)
        .options(
            joinedload(Doctor.user),
            selectinload(Doctor.working_hours),
        )
        .order_by(Doctor.id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    doctors = result.unique().scalars().all()

    return DoctorListResponse(
        items=[_doctor_to_response(d) for d in doctors],
        total=total,
        skip=skip,
        limit=limit,
    )


async def get_doctor(db: AsyncSession, doctor_id: int) -> DoctorResponse:
    stmt = (
        select(Doctor)
        .where(Doctor.id == doctor_id)
        .options(
            joinedload(Doctor.user),
            selectinload(Doctor.working_hours),
        )
    )
    result = await db.execute(stmt)
    doctor = result.unique().scalar_one_or_none()
    if doctor is None:
        raise NotFoundException(
            code="DOCTOR_NOT_FOUND",
            message="No doctor found with the given id.",
        )
    return _doctor_to_response(doctor)

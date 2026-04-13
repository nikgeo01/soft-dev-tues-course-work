from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.models import Appointment
from app.appointments.schemas import (
    AppointmentCreateRequest,
    AppointmentListFilters,
    AppointmentListResponse,
    AppointmentResponse,
)
from app.auth.models import User
from app.common.exceptions import (
    BusinessRuleException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.patients.models import Patient
from app.schedules.service import get_effective_schedule
from app.schedules.slot_fitting import appointment_interval_fits_working_slots


def _to_response(appointment: Appointment) -> AppointmentResponse:
    return AppointmentResponse.model_validate(appointment)


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def create_appointment(
    db: AsyncSession,
    patient_id: int,
    data: AppointmentCreateRequest,
) -> AppointmentResponse:
    patient_result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = patient_result.scalar_one_or_none()
    if patient is None:
        raise NotFoundException(
            code="PATIENT_NOT_FOUND",
            message="Patient profile not found.",
        )

    if data.doctor_id != patient.doctor_id:
        raise ForbiddenException(
            code="NOT_PERSONAL_DOCTOR",
            message="Appointments can only be created with your personal doctor.",
        )

    start_dt = _as_utc(data.start_datetime)
    end_dt = _as_utc(data.end_datetime)

    if end_dt <= start_dt:
        raise BusinessRuleException(
            code="INVALID_TIME_RANGE",
            message="end_datetime must be after start_datetime.",
        )

    now_utc = datetime.now(timezone.utc)
    if start_dt < now_utc + timedelta(hours=24):
        raise BusinessRuleException(
            code="TOO_SOON",
            message="Appointments must be created at least 24 hours in advance.",
        )

    if start_dt.date() != end_dt.date():
        raise BusinessRuleException(
            code="INVALID_TIME_RANGE",
            message="Appointment start and end must be on the same day.",
        )

    effective_slots = await get_effective_schedule(db, data.doctor_id, start_dt.date())
    if not appointment_interval_fits_working_slots(start_dt, end_dt, effective_slots):
        raise BusinessRuleException(
            code="OUTSIDE_WORKING_HOURS",
            message="Appointment is outside the doctor's effective working hours.",
        )

    overlap_result = await db.execute(
        select(func.count())
        .select_from(Appointment)
        .where(
            Appointment.doctor_id == data.doctor_id,
            Appointment.status == "scheduled",
            Appointment.start_datetime < end_dt,
            Appointment.end_datetime > start_dt,
        )
    )
    if int(overlap_result.scalar_one()) > 0:
        raise ConflictException(
            code="APPOINTMENT_OVERLAP",
            message="The requested time slot overlaps with an existing appointment.",
        )

    appointment = Appointment(
        doctor_id=data.doctor_id,
        patient_id=patient_id,
        start_datetime=start_dt,
        end_datetime=end_dt,
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return _to_response(appointment)


async def cancel_appointment(
    db: AsyncSession,
    user: User,
    appointment_id: int,
) -> None:
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if appointment is None:
        raise NotFoundException(
            code="APPOINTMENT_NOT_FOUND",
            message="Appointment not found.",
        )

    if appointment.status != "scheduled":
        raise ConflictException(
            code="ALREADY_CANCELLED",
            message="Appointment is already cancelled.",
        )

    if user.id not in {appointment.patient_id, appointment.doctor_id}:
        raise ForbiddenException(
            code="NOT_APPOINTMENT_OWNER",
            message="You are not allowed to cancel this appointment.",
        )

    start_dt = _as_utc(appointment.start_datetime)
    if start_dt - datetime.now(timezone.utc) < timedelta(hours=12):
        raise BusinessRuleException(
            code="CANCELLATION_TOO_LATE",
            message="Cancellation must be at least 12 hours before the appointment.",
        )

    appointment.status = "cancelled"
    appointment.cancelled_by = user.role
    await db.commit()


async def list_appointments(
    db: AsyncSession,
    user: User,
    filters: AppointmentListFilters,
    skip: int,
    limit: int,
) -> AppointmentListResponse:
    stmt = select(Appointment)
    count_stmt = select(func.count()).select_from(Appointment)

    if user.role == "doctor":
        stmt = stmt.where(Appointment.doctor_id == user.id)
        count_stmt = count_stmt.where(Appointment.doctor_id == user.id)
    elif user.role == "patient":
        stmt = stmt.where(Appointment.patient_id == user.id)
        count_stmt = count_stmt.where(Appointment.patient_id == user.id)
    else:
        raise ForbiddenException(
            code="UNSUPPORTED_ROLE",
            message="Only doctors and patients can list appointments.",
        )

    if filters.status is not None:
        stmt = stmt.where(Appointment.status == filters.status)
        count_stmt = count_stmt.where(Appointment.status == filters.status)

    if filters.date_from is not None:
        stmt = stmt.where(Appointment.start_datetime >= filters.date_from)
        count_stmt = count_stmt.where(Appointment.start_datetime >= filters.date_from)

    if filters.date_to is not None:
        date_to_end = datetime.combine(
            filters.date_to,
            datetime.max.time(),
            tzinfo=timezone.utc,
        )
        stmt = stmt.where(Appointment.start_datetime <= date_to_end)
        count_stmt = count_stmt.where(Appointment.start_datetime <= date_to_end)

    total_result = await db.execute(count_stmt)
    total = int(total_result.scalar_one())

    result = await db.execute(
        stmt.order_by(Appointment.start_datetime.desc()).offset(skip).limit(limit)
    )
    appointments = result.scalars().all()
    return AppointmentListResponse(
        items=[_to_response(apt) for apt in appointments],
        total=total,
        skip=skip,
        limit=limit,
    )

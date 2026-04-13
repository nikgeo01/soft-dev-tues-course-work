from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import (
    BusinessRuleException,
    ConflictException,
    NotFoundException,
)
from app.database import async_session
from app.doctors.models import Doctor
from app.schedules.appointment_conflicts import (
    assert_scheduled_appointments_still_fit_effective_schedule,
)
from app.schedules.models import (
    PermanentChange,
    PermanentChangeHours,
    TemporaryOverride,
    TemporaryOverrideHours,
    WorkingHours,
)
from app.schedules.schemas import (
    PermanentChangeRequest,
    PermanentChangeResponse,
    TemporaryOverrideRequest,
    TemporaryOverrideResponse,
    TimeSlotResponse,
    WeeklyScheduleResponse,
    WorkingHoursUpdateRequest,
)


def _slot_to_response(
    slot: WorkingHours | TemporaryOverrideHours | PermanentChangeHours,
) -> TimeSlotResponse:
    return TimeSlotResponse(
        id=slot.id,
        day_of_week=slot.day_of_week,
        start_time=slot.start_time,
        end_time=slot.end_time,
        is_break=slot.is_break,
    )


def _sort_key(
    slot: WorkingHours | TemporaryOverrideHours | PermanentChangeHours,
) -> tuple[int, object]:
    return (slot.day_of_week, slot.start_time)


async def _ensure_doctor_exists(db: AsyncSession, doctor_id: int) -> None:
    doctor_result = await db.execute(select(Doctor.id).where(Doctor.id == doctor_id))
    if doctor_result.scalar_one_or_none() is None:
        raise NotFoundException(
            code="DOCTOR_NOT_FOUND",
            message="No doctor found with the given id.",
        )


async def get_working_hours(db: AsyncSession, doctor_id: int) -> WeeklyScheduleResponse:
    await _ensure_doctor_exists(db, doctor_id)
    result = await db.execute(
        select(WorkingHours)
        .where(WorkingHours.doctor_id == doctor_id)
        .order_by(WorkingHours.day_of_week, WorkingHours.start_time)
    )
    rows = result.scalars().all()
    return WeeklyScheduleResponse(items=[_slot_to_response(row) for row in rows])


async def update_working_hours(
    db: AsyncSession,
    doctor_id: int,
    data: WorkingHoursUpdateRequest,
) -> WeeklyScheduleResponse:
    await _ensure_doctor_exists(db, doctor_id)
    await db.execute(delete(WorkingHours).where(WorkingHours.doctor_id == doctor_id))
    for slot in data.slots:
        db.add(
            WorkingHours(
                doctor_id=doctor_id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                is_break=slot.is_break,
            )
        )
    await db.flush()
    try:
        await assert_scheduled_appointments_still_fit_effective_schedule(db, doctor_id)
    except BaseException:
        await db.rollback()
        raise
    await db.commit()
    return await get_working_hours(db, doctor_id)


async def create_temporary_override(
    db: AsyncSession,
    doctor_id: int,
    data: TemporaryOverrideRequest,
) -> TemporaryOverrideResponse:
    await _ensure_doctor_exists(db, doctor_id)
    if data.end_datetime <= data.start_datetime:
        raise BusinessRuleException(
            code="INVALID_OVERRIDE_WINDOW",
            message="Override end_datetime must be after start_datetime.",
        )

    existing_result = await db.execute(
        select(TemporaryOverride.id).where(TemporaryOverride.doctor_id == doctor_id)
    )
    if existing_result.scalar_one_or_none() is not None:
        raise ConflictException(
            code="OVERRIDE_EXISTS",
            message="Doctor already has an active temporary override.",
        )

    override = TemporaryOverride(
        doctor_id=doctor_id,
        start_datetime=data.start_datetime,
        end_datetime=data.end_datetime,
    )
    db.add(override)
    await db.flush()

    for slot in data.schedule:
        db.add(
            TemporaryOverrideHours(
                override_id=override.id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                is_break=slot.is_break,
            )
        )

    await db.flush()
    try:
        await assert_scheduled_appointments_still_fit_effective_schedule(db, doctor_id)
    except BaseException:
        await db.rollback()
        raise
    await db.commit()

    override_result = await db.execute(
        select(TemporaryOverride)
        .where(TemporaryOverride.id == override.id)
        .options(selectinload(TemporaryOverride.hours))
    )
    saved_override = override_result.scalar_one()
    sorted_hours = sorted(saved_override.hours, key=_sort_key)
    return TemporaryOverrideResponse(
        id=saved_override.id,
        start_datetime=saved_override.start_datetime,
        end_datetime=saved_override.end_datetime,
        schedule=[_slot_to_response(hour) for hour in sorted_hours],
    )


async def delete_temporary_override(db: AsyncSession, doctor_id: int) -> None:
    await _ensure_doctor_exists(db, doctor_id)
    result = await db.execute(
        select(TemporaryOverride).where(TemporaryOverride.doctor_id == doctor_id)
    )
    override = result.scalar_one_or_none()
    if override is None:
        raise NotFoundException(
            code="OVERRIDE_NOT_FOUND",
            message="No temporary override found for this doctor.",
        )
    await db.delete(override)
    await db.commit()


async def get_effective_schedule(
    db: AsyncSession,
    doctor_id: int,
    target_date: date,
) -> list[TimeSlotResponse]:
    await _ensure_doctor_exists(db, doctor_id)
    async with async_session() as promotion_session:
        await apply_pending_permanent_changes(promotion_session)
    weekday = target_date.weekday()
    day_start = datetime.combine(target_date, datetime.min.time())

    override_result = await db.execute(
        select(TemporaryOverride)
        .where(
            TemporaryOverride.doctor_id == doctor_id,
            TemporaryOverride.start_datetime <= day_start,
            TemporaryOverride.end_datetime >= day_start,
        )
        .options(selectinload(TemporaryOverride.hours))
    )
    override = override_result.scalar_one_or_none()
    if override is not None:
        slots = [hour for hour in override.hours if hour.day_of_week == weekday]
        slots.sort(key=_sort_key)
        return [_slot_to_response(slot) for slot in slots]

    perm_result = await db.execute(
        select(PermanentChange)
        .where(
            PermanentChange.doctor_id == doctor_id,
            PermanentChange.effective_date <= target_date,
        )
        .order_by(PermanentChange.effective_date.desc())
        .options(selectinload(PermanentChange.hours))
        .limit(1)
    )
    permanent_change = perm_result.scalar_one_or_none()
    if permanent_change is not None:
        perm_slots = [
            hour for hour in permanent_change.hours if hour.day_of_week == weekday
        ]
        perm_slots.sort(key=_sort_key)
        return [_slot_to_response(slot) for slot in perm_slots]

    base_result = await db.execute(
        select(WorkingHours)
        .where(
            WorkingHours.doctor_id == doctor_id,
            WorkingHours.day_of_week == weekday,
        )
        .order_by(WorkingHours.start_time)
    )
    base_slots = base_result.scalars().all()
    return [_slot_to_response(slot) for slot in base_slots]


async def create_permanent_change(
    db: AsyncSession,
    doctor_id: int,
    data: PermanentChangeRequest,
) -> PermanentChangeResponse:
    await _ensure_doctor_exists(db, doctor_id)
    min_effective_date = date.today() + timedelta(days=7)
    if data.effective_date < min_effective_date:
        raise BusinessRuleException(
            code="EFFECTIVE_DATE_TOO_SOON",
            message="Permanent changes must be scheduled at least 7 days ahead.",
        )

    change = PermanentChange(
        doctor_id=doctor_id,
        effective_date=data.effective_date,
    )
    db.add(change)
    await db.flush()

    for slot in data.schedule:
        db.add(
            PermanentChangeHours(
                change_id=change.id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                is_break=slot.is_break,
            )
        )

    await db.flush()
    try:
        await assert_scheduled_appointments_still_fit_effective_schedule(db, doctor_id)
    except BaseException:
        await db.rollback()
        raise
    await db.commit()

    change_result = await db.execute(
        select(PermanentChange)
        .where(PermanentChange.id == change.id)
        .options(selectinload(PermanentChange.hours))
    )
    saved_change = change_result.scalar_one()
    sorted_hours = sorted(saved_change.hours, key=_sort_key)
    return PermanentChangeResponse(
        id=saved_change.id,
        effective_date=saved_change.effective_date,
        applied=saved_change.applied,
        schedule=[_slot_to_response(hour) for hour in sorted_hours],
    )


async def apply_pending_permanent_changes(db: AsyncSession) -> None:
    today = date.today()
    changes_result = await db.execute(
        select(PermanentChange)
        .where(
            PermanentChange.applied.is_(False),
            PermanentChange.effective_date <= today,
        )
        .options(selectinload(PermanentChange.hours))
        .order_by(PermanentChange.effective_date.asc(), PermanentChange.id.asc())
    )
    changes = changes_result.scalars().all()

    for change in changes:
        await db.execute(
            delete(WorkingHours).where(WorkingHours.doctor_id == change.doctor_id)
        )
        for slot in change.hours:
            db.add(
                WorkingHours(
                    doctor_id=change.doctor_id,
                    day_of_week=slot.day_of_week,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    is_break=slot.is_break,
                )
            )
        change.applied = True

    await db.commit()

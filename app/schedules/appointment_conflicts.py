from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.models import Appointment
from app.common.exceptions import BusinessRuleException
from app.schedules.slot_fitting import appointment_interval_fits_working_slots


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def assert_scheduled_appointments_still_fit_effective_schedule(
    db: AsyncSession,
    doctor_id: int,
) -> None:
    """Raise if a scheduled appointment no longer fits the effective schedule."""
    from app.schedules.service import get_effective_schedule

    result = await db.execute(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "scheduled",
        )
    )
    appointments = result.scalars().all()
    for appt in appointments:
        start_dt = _as_utc(appt.start_datetime)
        end_dt = _as_utc(appt.end_datetime)
        if start_dt.date() != end_dt.date() or end_dt <= start_dt:
            raise BusinessRuleException(
                code="SCHEDULE_CONFLICTS_APPOINTMENT",
                message=(
                    "This schedule change conflicts with existing appointments "
                    f"(appointment id={appt.id})."
                ),
            )
        day = start_dt.date()
        slots = await get_effective_schedule(db, doctor_id, day)
        if not appointment_interval_fits_working_slots(start_dt, end_dt, slots):
            raise BusinessRuleException(
                code="SCHEDULE_CONFLICTS_APPOINTMENT",
                message=(
                    "This schedule change would leave scheduled appointments "
                    "outside working hours."
                ),
            )

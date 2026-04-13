from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, time

from app.schedules.schemas import TimeSlotResponse


def appointment_interval_fits_working_slots(
    start_dt: datetime,
    end_dt: datetime,
    slots: Sequence[TimeSlotResponse],
) -> bool:
    """True if the interval fits in one non-break slot (same as create_appointment)."""
    if start_dt.date() != end_dt.date() or end_dt <= start_dt:
        return False
    start_time: time = start_dt.timetz().replace(tzinfo=None)
    end_time: time = end_dt.timetz().replace(tzinfo=None)
    return any(
        (not slot.is_break)
        and slot.start_time <= start_time
        and slot.end_time >= end_time
        for slot in slots
    )

from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class TimeSlot(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    is_break: bool = False


class TimeSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_of_week: int
    start_time: time
    end_time: time
    is_break: bool


class WeeklyScheduleResponse(BaseModel):
    items: list[TimeSlotResponse]


class WorkingHoursUpdateRequest(BaseModel):
    slots: list[TimeSlot]


class TemporaryOverrideRequest(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    schedule: list[TimeSlot]


class TemporaryOverrideResponse(BaseModel):
    id: int
    start_datetime: datetime
    end_datetime: datetime
    schedule: list[TimeSlotResponse]


class PermanentChangeRequest(BaseModel):
    effective_date: date
    schedule: list[TimeSlot]


class PermanentChangeResponse(BaseModel):
    id: int
    effective_date: date
    applied: bool
    schedule: list[TimeSlotResponse]

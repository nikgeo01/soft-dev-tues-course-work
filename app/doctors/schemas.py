from __future__ import annotations

from datetime import time

from pydantic import BaseModel, ConfigDict


class WorkingHoursResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_of_week: int
    start_time: time
    end_time: time
    is_break: bool


class DoctorResponse(BaseModel):
    id: int
    name: str
    email: str
    address: str
    working_hours: list[WorkingHoursResponse]


class DoctorListResponse(BaseModel):
    items: list[DoctorResponse]
    total: int
    skip: int
    limit: int

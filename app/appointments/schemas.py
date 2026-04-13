from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreateRequest(BaseModel):
    doctor_id: int = Field(gt=0)
    start_datetime: datetime
    end_datetime: datetime


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    patient_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    cancelled_by: Optional[str]  # noqa: UP045


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
    skip: int
    limit: int


class AppointmentListFilters(BaseModel):
    date_from: Optional[date] = None  # noqa: UP045
    date_to: Optional[date] = None  # noqa: UP045
    status: Optional[str] = None  # noqa: UP045

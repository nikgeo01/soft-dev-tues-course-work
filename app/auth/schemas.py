from __future__ import annotations

from datetime import time

from pydantic import BaseModel, EmailStr, Field


class WorkingHoursSlot(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    is_break: bool = False


class DoctorRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    address: str = Field(min_length=1, max_length=512)
    working_hours: list[WorkingHoursSlot]


class PatientRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str = Field(min_length=1, max_length=64)
    doctor_id: int = Field(gt=0)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

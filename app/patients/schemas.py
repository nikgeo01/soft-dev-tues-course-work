from __future__ import annotations

from pydantic import BaseModel


class PatientResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    doctor_id: int

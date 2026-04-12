from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.common.exceptions import NotFoundException
from app.patients.models import Patient
from app.patients.schemas import PatientResponse


async def get_patient_profile(db: AsyncSession, patient_id: int) -> PatientResponse:
    stmt = (
        select(Patient)
        .where(Patient.id == patient_id)
        .options(joinedload(Patient.user))
    )
    result = await db.execute(stmt)
    patient = result.unique().scalar_one_or_none()
    if patient is None:
        raise NotFoundException(
            code="PATIENT_NOT_FOUND",
            message="Patient profile not found.",
        )
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        email=patient.user.email,
        phone=patient.phone,
        doctor_id=patient.doctor_id,
    )

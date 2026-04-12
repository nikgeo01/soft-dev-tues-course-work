from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.dependencies import get_db, require_patient
from app.patients.schemas import PatientResponse
from app.patients.service import get_patient_profile

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientResponse)
async def get_my_patient_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_patient)],
) -> PatientResponse:
    return await get_patient_profile(db, user.id)

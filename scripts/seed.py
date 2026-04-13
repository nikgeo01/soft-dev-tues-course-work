#!/usr/bin/env python3
"""Insert demo doctor + patient into the configured database (dev only).

Uses passwords from constants below — change them after first login in real deployments.
Run from repo root after `pip install -e ".[dev]"` and `make migrate`:

    make seed
    # or: python scripts/seed.py
"""

from __future__ import annotations

import asyncio
from datetime import time

from sqlalchemy import select

from app.auth.models import User
from app.auth.schemas import (
    DoctorRegisterRequest,
    PatientRegisterRequest,
    WorkingHoursSlot,
)
from app.auth.service import register_doctor, register_patient
from app.database import async_session
from app.doctors.models import Doctor

# Dev-only credentials (documented here intentionally for local demos).
SEED_DOCTOR_EMAIL = "seed-doctor@example.local"
SEED_DOCTOR_PASSWORD = "seed-doctor-password-change-me"
SEED_PATIENT_EMAIL = "seed-patient@example.local"
SEED_PATIENT_PASSWORD = "seed-patient-password-change-me"


def _weekday_slots() -> list[WorkingHoursSlot]:
    return [
        WorkingHoursSlot(
            day_of_week=d,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_break=False,
        )
        for d in range(5)
    ]


async def main() -> None:
    doctor_req = DoctorRegisterRequest(
        name="Dr. Seed",
        email=SEED_DOCTOR_EMAIL,
        password=SEED_DOCTOR_PASSWORD,
        address="1 Seed Street",
        working_hours=_weekday_slots(),
    )
    async with async_session() as session:
        await register_doctor(session, doctor_req)

    async with async_session() as session:
        dr = await session.execute(
            select(Doctor.id)
            .join(User, User.id == Doctor.id)
            .where(User.email == SEED_DOCTOR_EMAIL)
        )
        doctor_id = dr.scalar_one()
        patient_req = PatientRegisterRequest(
            name="Seed Patient",
            email=SEED_PATIENT_EMAIL,
            password=SEED_PATIENT_PASSWORD,
            phone="+10000000000",
            doctor_id=doctor_id,
        )
        await register_patient(session, patient_req)

    print("Seed complete.")
    print(f"  Doctor: {SEED_DOCTOR_EMAIL} / {SEED_DOCTOR_PASSWORD}")
    print(f"  Patient: {SEED_PATIENT_EMAIL} / {SEED_PATIENT_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())

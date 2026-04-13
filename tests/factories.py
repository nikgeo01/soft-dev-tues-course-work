from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from httpx import AsyncClient

DEFAULT_WORKING_HOURS = [
    {
        "day_of_week": day,
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "is_break": False,
    }
    for day in range(5)
]

DEFAULT_DOCTOR_REGISTRATION = {
    "name": "Dr. Test",
    "email": "doctor@example.com",
    "password": "password123",
    "address": "Test Address 1",
    "working_hours": DEFAULT_WORKING_HOURS,
}

DEFAULT_PATIENT_REGISTRATION = {
    "name": "Patient Test",
    "email": "patient@example.com",
    "password": "password123",
    "phone": "+359888000000",
}


def unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@example.com"


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_working_hours_payload() -> list[dict[str, object]]:
    return [
        {
            "day_of_week": day,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_break": False,
        }
        for day in range(5)
    ]


def create_appointment_payload(
    doctor_id: int, hours_from_now: int = 48
) -> dict[str, str | int]:
    start = datetime.now(timezone.utc) + timedelta(hours=hours_from_now)
    end = start + timedelta(hours=1)
    return {
        "doctor_id": doctor_id,
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
    }


async def register_doctor(
    client: AsyncClient,
    **overrides,
) -> tuple[str, int]:
    payload = {
        **DEFAULT_DOCTOR_REGISTRATION,
        "email": unique_email("doctor"),
        **overrides,
    }
    resp = await client.post("/auth/register/doctor", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    login_resp = await client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_resp.status_code == 200, login_resp.text
    # Doctor id equals user id, infer by decoding protected endpoint list first item
    doctors_resp = await client.get("/doctors")
    assert doctors_resp.status_code == 200, doctors_resp.text
    created_doctor = next(
        d for d in doctors_resp.json()["items"] if d["email"] == payload["email"]
    )
    return token, int(created_doctor["id"])


async def register_patient(
    client: AsyncClient,
    doctor_id: int,
    **overrides,
) -> tuple[str, int]:
    payload = {
        **DEFAULT_PATIENT_REGISTRATION,
        "email": unique_email("patient"),
        "doctor_id": doctor_id,
        **overrides,
    }
    resp = await client.post("/auth/register/patient", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    profile_resp = await client.get("/patients/me", headers=auth_header(token))
    assert profile_resp.status_code == 200, profile_resp.text
    return token, int(profile_resp.json()["id"])

from datetime import datetime, timedelta, timezone

from httpx import AsyncClient

from tests.factories import (
    auth_header,
    create_appointment_payload,
    register_doctor,
    register_patient,
)


async def test_create_appointment_success(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    resp = await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_id),
        headers=auth_header(patient_token),
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "scheduled"


async def test_create_with_non_personal_doctor(client: AsyncClient) -> None:
    _doc1_token, doctor_1_id = await register_doctor(client)
    _doc2_token, doctor_2_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_1_id)
    resp = await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_2_id),
        headers=auth_header(patient_token),
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "NOT_PERSONAL_DOCTOR"


async def test_create_outside_working_hours(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    start = datetime.now(timezone.utc) + timedelta(hours=48)
    start = start.replace(hour=22, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    payload = {
        "doctor_id": doctor_id,
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
    }
    resp = await client.post(
        "/appointments",
        json=payload,
        headers=auth_header(patient_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "OUTSIDE_WORKING_HOURS"


async def test_create_less_than_24h(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    resp = await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_id, hours_from_now=2),
        headers=auth_header(patient_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "TOO_SOON"


async def test_create_overlapping(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    start = datetime.now(timezone.utc) + timedelta(hours=72)
    start = start.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    first_payload = {
        "doctor_id": doctor_id,
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
    }
    first = await client.post(
        "/appointments",
        json=first_payload,
        headers=auth_header(patient_token),
    )
    assert first.status_code == 201

    second_start = datetime.fromisoformat(first_payload["start_datetime"]) + timedelta(
        minutes=30
    )
    second_end = second_start + timedelta(hours=1)
    second = await client.post(
        "/appointments",
        json={
            "doctor_id": doctor_id,
            "start_datetime": second_start.isoformat(),
            "end_datetime": second_end.isoformat(),
        },
        headers=auth_header(patient_token),
    )
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "APPOINTMENT_OVERLAP"

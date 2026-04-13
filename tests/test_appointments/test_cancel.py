from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.models import Appointment
from tests.factories import (
    auth_header,
    create_appointment_payload,
    register_doctor,
    register_patient,
)


async def test_cancel_by_patient_success(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    created = await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_id),
        headers=auth_header(patient_token),
    )
    appointment_id = created.json()["id"]
    resp = await client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_header(patient_token),
    )
    assert resp.status_code == 204


async def test_cancel_by_doctor_success(client: AsyncClient) -> None:
    doctor_token, doctor_id = await register_doctor(client)
    patient_token, patient_id = await register_patient(client, doctor_id)
    _ = patient_id
    created = await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_id),
        headers=auth_header(patient_token),
    )
    appointment_id = created.json()["id"]
    resp = await client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 204


async def test_cancel_already_cancelled(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    created = await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_id),
        headers=auth_header(patient_token),
    )
    appointment_id = created.json()["id"]
    first = await client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_header(patient_token),
    )
    assert first.status_code == 204
    second = await client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_header(patient_token),
    )
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "ALREADY_CANCELLED"


async def test_cancel_less_than_12h(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, patient_id = await register_patient(client, doctor_id)
    appt = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        start_datetime=datetime.now(timezone.utc) + timedelta(hours=4),
        end_datetime=datetime.now(timezone.utc) + timedelta(hours=5),
        status="scheduled",
    )
    db_session.add(appt)
    await db_session.commit()
    await db_session.refresh(appt)

    resp = await client.delete(
        f"/appointments/{appt.id}",
        headers=auth_header(patient_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "CANCELLATION_TOO_LATE"

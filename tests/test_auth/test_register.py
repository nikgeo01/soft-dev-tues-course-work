from httpx import AsyncClient

from tests.factories import register_doctor, unique_email


async def test_register_doctor_success(client: AsyncClient) -> None:
    payload = {
        "name": "Dr. Alpha",
        "email": unique_email("doctor-register"),
        "password": "password123",
        "address": "Main Street 1",
        "working_hours": [
            {
                "day_of_week": 0,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "is_break": False,
            }
        ],
    }
    resp = await client.post("/auth/register/doctor", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_register_patient_success(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    payload = {
        "name": "Patient Alpha",
        "email": unique_email("patient-register"),
        "password": "password123",
        "phone": "+359888111111",
        "doctor_id": doctor_id,
    }
    resp = await client.post("/auth/register/patient", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_register_duplicate_email(client: AsyncClient) -> None:
    email = unique_email("dup-email")
    payload = {
        "name": "Dr. Dup",
        "email": email,
        "password": "password123",
        "address": "Dup Street 5",
        "working_hours": [
            {
                "day_of_week": 0,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "is_break": False,
            }
        ],
    }
    first = await client.post("/auth/register/doctor", json=payload)
    assert first.status_code == 201
    second = await client.post("/auth/register/doctor", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "EMAIL_EXISTS"

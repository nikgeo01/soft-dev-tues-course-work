from httpx import AsyncClient

from tests.factories import auth_header, register_doctor, register_patient


async def test_patients_me_success(client: AsyncClient) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    patient_token, patient_id = await register_patient(client, doctor_id)
    resp = await client.get("/patients/me", headers=auth_header(patient_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == patient_id
    assert data["doctor_id"] == doctor_id


async def test_patients_me_without_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/patients/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

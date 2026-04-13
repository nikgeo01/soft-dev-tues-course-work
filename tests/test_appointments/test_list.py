from httpx import AsyncClient

from tests.factories import (
    auth_header,
    create_appointment_payload,
    register_doctor,
    register_patient,
)


async def test_list_returns_own_only(client: AsyncClient) -> None:
    doctor_1_token, doctor_1_id = await register_doctor(client)
    patient_1_token, _patient_1_id = await register_patient(client, doctor_1_id)

    doctor_2_token, doctor_2_id = await register_doctor(client)
    patient_2_token, _patient_2_id = await register_patient(client, doctor_2_id)

    await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_1_id),
        headers=auth_header(patient_1_token),
    )
    await client.post(
        "/appointments",
        json=create_appointment_payload(doctor_2_id),
        headers=auth_header(patient_2_token),
    )

    doctor_list = await client.get("/appointments", headers=auth_header(doctor_1_token))
    assert doctor_list.status_code == 200
    assert doctor_list.json()["total"] == 1

    patient_list = await client.get(
        "/appointments", headers=auth_header(patient_1_token)
    )
    assert patient_list.status_code == 200
    assert patient_list.json()["total"] == 1

    other_doctor_list = await client.get(
        "/appointments", headers=auth_header(doctor_2_token)
    )
    assert other_doctor_list.status_code == 200
    assert other_doctor_list.json()["total"] == 1

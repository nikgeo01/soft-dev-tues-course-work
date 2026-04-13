from datetime import date, timedelta

from httpx import AsyncClient

from tests.factories import auth_header, create_working_hours_payload, register_doctor


async def test_update_base_schedule_success(client: AsyncClient) -> None:
    doctor_token, _doctor_id = await register_doctor(client)
    payload = {"slots": create_working_hours_payload()}
    resp = await client.put(
        "/doctors/me/schedule",
        json=payload,
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 5


async def test_get_effective_schedule_returns_base(client: AsyncClient) -> None:
    doctor_token, doctor_id = await register_doctor(client)
    payload = {"slots": create_working_hours_payload()}
    await client.put(
        "/doctors/me/schedule", json=payload, headers=auth_header(doctor_token)
    )

    monday = date.today() + timedelta(days=(7 - date.today().weekday()) % 7)
    resp = await client.get(
        f"/doctors/{doctor_id}/schedule", params={"date": monday.isoformat()}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["start_time"] == "09:00:00"

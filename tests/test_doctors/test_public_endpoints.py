from httpx import AsyncClient

from tests.factories import register_doctor


async def test_list_doctors_returns_paginated_shape(client: AsyncClient) -> None:
    await register_doctor(client)
    resp = await client.get("/doctors")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "skip" in body
    assert "limit" in body
    assert isinstance(body["items"], list)


async def test_get_doctor_detail_success(client: AsyncClient) -> None:
    _token, doctor_id = await register_doctor(client)
    resp = await client.get(f"/doctors/{doctor_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == doctor_id
    assert "working_hours" in data


async def test_get_doctor_not_found(client: AsyncClient) -> None:
    resp = await client.get("/doctors/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "DOCTOR_NOT_FOUND"

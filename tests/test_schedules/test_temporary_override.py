from datetime import date, datetime, time, timedelta, timezone

from httpx import AsyncClient

from tests.factories import auth_header, create_working_hours_payload, register_doctor


def _override_payload(target_date: date) -> dict[str, object]:
    start = datetime.combine(target_date, time.min, tzinfo=timezone.utc) - timedelta(
        hours=1
    )
    end = start + timedelta(days=2)
    return {
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
        "schedule": [
            {
                "day_of_week": target_date.weekday(),
                "start_time": "11:00:00",
                "end_time": "15:00:00",
                "is_break": False,
            }
        ],
    }


async def test_create_temporary_override_success(client: AsyncClient) -> None:
    doctor_token, _doctor_id = await register_doctor(client)
    target_date = date.today() + timedelta(days=1)
    resp = await client.post(
        "/doctors/me/schedule/temporary",
        json=_override_payload(target_date),
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 201
    assert len(resp.json()["schedule"]) == 1


async def test_create_second_override_conflict(client: AsyncClient) -> None:
    doctor_token, _doctor_id = await register_doctor(client)
    target_date = date.today() + timedelta(days=2)
    payload = _override_payload(target_date)
    first = await client.post(
        "/doctors/me/schedule/temporary",
        json=payload,
        headers=auth_header(doctor_token),
    )
    assert first.status_code == 201
    second = await client.post(
        "/doctors/me/schedule/temporary",
        json=payload,
        headers=auth_header(doctor_token),
    )
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "OVERRIDE_EXISTS"


async def test_delete_temporary_override_success(client: AsyncClient) -> None:
    doctor_token, _doctor_id = await register_doctor(client)
    target_date = date.today() + timedelta(days=2)
    await client.post(
        "/doctors/me/schedule/temporary",
        json=_override_payload(target_date),
        headers=auth_header(doctor_token),
    )
    resp = await client.delete(
        "/doctors/me/schedule/temporary",
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 204


async def test_schedule_resolution_with_override(client: AsyncClient) -> None:
    doctor_token, doctor_id = await register_doctor(client)
    await client.put(
        "/doctors/me/schedule",
        json={"slots": create_working_hours_payload()},
        headers=auth_header(doctor_token),
    )
    target_date = date.today() + timedelta(days=3)
    await client.post(
        "/doctors/me/schedule/temporary",
        json=_override_payload(target_date),
        headers=auth_header(doctor_token),
    )
    resp = await client.get(
        f"/doctors/{doctor_id}/schedule",
        params={"date": target_date.isoformat()},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["start_time"] == "11:00:00"

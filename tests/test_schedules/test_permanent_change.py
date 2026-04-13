from datetime import date, time, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schedules.models import PermanentChange, PermanentChangeHours
from tests.factories import auth_header, register_doctor


def _schedule(day_of_week: int, start: str, end: str) -> list[dict[str, object]]:
    return [
        {
            "day_of_week": day_of_week,
            "start_time": start,
            "end_time": end,
            "is_break": False,
        }
    ]


async def test_create_permanent_change_success(client: AsyncClient) -> None:
    doctor_token, _doctor_id = await register_doctor(client)
    effective_date = date.today() + timedelta(days=8)
    resp = await client.post(
        "/doctors/me/schedule/permanent",
        json={
            "effective_date": effective_date.isoformat(),
            "schedule": _schedule(0, "10:00:00", "16:00:00"),
        },
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 201
    assert resp.json()["effective_date"] == effective_date.isoformat()


async def test_permanent_change_too_soon(client: AsyncClient) -> None:
    doctor_token, _doctor_id = await register_doctor(client)
    too_soon = date.today() + timedelta(days=1)
    resp = await client.post(
        "/doctors/me/schedule/permanent",
        json={
            "effective_date": too_soon.isoformat(),
            "schedule": _schedule(0, "10:00:00", "16:00:00"),
        },
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "EFFECTIVE_DATE_TOO_SOON"


async def test_schedule_resolution_with_permanent_change(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    _doctor_token, doctor_id = await register_doctor(client)
    target_date = date.today()
    change = PermanentChange(
        doctor_id=doctor_id, effective_date=target_date, applied=False
    )
    db_session.add(change)
    await db_session.flush()
    db_session.add(
        PermanentChangeHours(
            change_id=change.id,
            day_of_week=target_date.weekday(),
            start_time=time(12, 0),
            end_time=time(13, 0),
            is_break=False,
        )
    )
    await db_session.commit()

    resp = await client.get(
        f"/doctors/{doctor_id}/schedule", params={"date": target_date.isoformat()}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["start_time"] == "12:00:00"

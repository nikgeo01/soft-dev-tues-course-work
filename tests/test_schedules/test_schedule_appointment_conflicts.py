from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from httpx import AsyncClient

from tests.factories import auth_header, register_doctor, register_patient


def _weekday_slots(weekday: int, start: str, end: str) -> list[dict[str, object]]:
    return [
        {
            "day_of_week": weekday,
            "start_time": start,
            "end_time": end,
            "is_break": False,
        }
    ]


def _default_weekly_slots(
    except_day: int, replacement: dict[str, object]
) -> list[dict]:
    slots: list[dict] = []
    for day in range(5):
        if day == except_day:
            slots.append(replacement)
        else:
            slots.append(
                {
                    "day_of_week": day,
                    "start_time": "09:00:00",
                    "end_time": "17:00:00",
                    "is_break": False,
                }
            )
    return slots


async def test_update_base_schedule_rejected_when_appointment_no_longer_fits(
    client: AsyncClient,
) -> None:
    doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    start = datetime.now(timezone.utc) + timedelta(hours=72)
    start = start.replace(hour=10, minute=0, second=0, microsecond=0)
    while start.weekday() > 4:
        start += timedelta(days=1)
    end = start + timedelta(hours=1)
    book = await client.post(
        "/appointments",
        json={
            "doctor_id": doctor_id,
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
        },
        headers=auth_header(patient_token),
    )
    assert book.status_code == 201, book.text

    wd = start.weekday()
    payload = {
        "slots": _default_weekly_slots(
            wd,
            {
                "day_of_week": wd,
                "start_time": "14:00:00",
                "end_time": "17:00:00",
                "is_break": False,
            },
        )
    }
    resp = await client.put(
        "/doctors/me/schedule",
        json=payload,
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "SCHEDULE_CONFLICTS_APPOINTMENT"


async def test_temporary_override_rejected_when_appointment_not_in_override_slots(
    client: AsyncClient,
) -> None:
    doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    start = datetime.now(timezone.utc) + timedelta(hours=72)
    start = start.replace(hour=10, minute=0, second=0, microsecond=0)
    while start.weekday() > 4:
        start += timedelta(days=1)
    end = start + timedelta(hours=1)
    book = await client.post(
        "/appointments",
        json={
            "doctor_id": doctor_id,
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
        },
        headers=auth_header(patient_token),
    )
    assert book.status_code == 201, book.text

    target_date = start.date()
    override_start = datetime.combine(
        target_date, time.min, tzinfo=timezone.utc
    ) - timedelta(hours=1)
    override_end = override_start + timedelta(days=2)
    wd = start.weekday()
    resp = await client.post(
        "/doctors/me/schedule/temporary",
        json={
            "start_datetime": override_start.isoformat(),
            "end_datetime": override_end.isoformat(),
            "schedule": _weekday_slots(wd, "12:00:00", "13:00:00"),
        },
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "SCHEDULE_CONFLICTS_APPOINTMENT"


async def test_permanent_change_rejected_when_appointment_not_in_new_schedule(
    client: AsyncClient,
) -> None:
    doctor_token, doctor_id = await register_doctor(client)
    patient_token, _patient_id = await register_patient(client, doctor_id)
    effective_date = date.today() + timedelta(days=10)
    while effective_date.weekday() > 4:
        effective_date += timedelta(days=1)
    start = datetime.combine(effective_date, time(10, 0), tzinfo=timezone.utc)
    if start < datetime.now(timezone.utc) + timedelta(hours=24):
        effective_date += timedelta(days=7)
        while effective_date.weekday() > 4:
            effective_date += timedelta(days=1)
        start = datetime.combine(effective_date, time(10, 0), tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    book = await client.post(
        "/appointments",
        json={
            "doctor_id": doctor_id,
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
        },
        headers=auth_header(patient_token),
    )
    assert book.status_code == 201, book.text

    wd = effective_date.weekday()
    resp = await client.post(
        "/doctors/me/schedule/permanent",
        json={
            "effective_date": effective_date.isoformat(),
            "schedule": _weekday_slots(wd, "12:00:00", "13:00:00"),
        },
        headers=auth_header(doctor_token),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "SCHEDULE_CONFLICTS_APPOINTMENT"

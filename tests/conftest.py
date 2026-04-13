from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.auth.service as auth_service
import app.database as app_database
from app.database import Base
from app.dependencies import get_db
from app.main import create_app
from tests.factories import (
    DEFAULT_DOCTOR_REGISTRATION,
    DEFAULT_PATIENT_REGISTRATION,
    register_doctor,
    register_patient,
)

AuthenticatedClientFactory = Callable[..., Awaitable[AsyncClient]]


@pytest_asyncio.fixture
async def test_engine() -> AsyncGenerator:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
    monkeypatch,
) -> AsyncGenerator[AsyncClient, None]:
    # Schedule promotion uses `async_session()` in a side session; align with test DB.
    monkeypatch.setattr(app_database, "async_session", session_factory)

    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AuthenticatedClientFactory:
    async def _factory(role: str = "doctor", **overrides) -> AsyncClient:
        if role == "doctor":
            doctor_data = {**DEFAULT_DOCTOR_REGISTRATION, **overrides}
            token, _doctor_id = await register_doctor(client, **doctor_data)
        elif role == "patient":
            doctor_token, doctor_id = await register_doctor(
                client, **DEFAULT_DOCTOR_REGISTRATION
            )
            _ = doctor_token
            patient_data = {
                **DEFAULT_PATIENT_REGISTRATION,
                "doctor_id": doctor_id,
                **overrides,
            }
            token, _patient_id = await register_patient(client, **patient_data)
        else:
            raise ValueError("role must be 'doctor' or 'patient'")

        client.headers.update({"Authorization": f"Bearer {token}"})
        return client

    return _factory


@pytest_asyncio.fixture(autouse=True)
async def _mock_password_hashing(monkeypatch) -> None:
    monkeypatch.setattr(auth_service, "hash_password", lambda plain: f"hashed::{plain}")
    monkeypatch.setattr(
        auth_service,
        "verify_password",
        lambda plain, hashed: hashed == f"hashed::{plain}",
    )

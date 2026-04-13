from httpx import AsyncClient

from tests.factories import register_doctor, unique_email


async def test_login_success(client: AsyncClient) -> None:
    email = unique_email("doctor-login")
    password = "password123"
    await register_doctor(client, email=email, password=password)
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient) -> None:
    email = unique_email("doctor-login-fail")
    await register_doctor(client, email=email, password="password123")
    resp = await client.post(
        "/auth/login", json={"email": email, "password": "wrong-password"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "INVALID_CREDENTIALS"


async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    resp = await client.get("/patients/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

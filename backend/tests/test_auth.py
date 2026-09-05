import pytest

pytestmark = pytest.mark.asyncio


async def test_register_and_login(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "founder@shreecodemantra.com", "password": "supersecret123", "full_name": "Founder"},
    )
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["email"] == "founder@shreecodemantra.com"

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "founder@shreecodemantra.com", "password": "supersecret123"},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens


async def test_duplicate_registration_rejected(client):
    payload = {"email": "dup@shreecodemantra.com", "password": "supersecret123"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "ALREADY_EXISTS"


async def test_login_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/register", json={"email": "wrongpw@shreecodemantra.com", "password": "correctpassword"}
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpw@shreecodemantra.com", "password": "incorrect"},
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_me_with_token(client):
    await client.post(
        "/api/v1/auth/register", json={"email": "me@shreecodemantra.com", "password": "supersecret123"}
    )
    login_resp = await client.post(
        "/api/v1/auth/login", data={"username": "me@shreecodemantra.com", "password": "supersecret123"}
    )
    token = login_resp.json()["access_token"]

    resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@shreecodemantra.com"

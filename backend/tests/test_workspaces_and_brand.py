import pytest

pytestmark = pytest.mark.asyncio


async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return resp.json()["access_token"]


async def test_create_workspace_and_manage_brand(client):
    token = await _register_and_login(client, "owner@shreecodemantra.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/workspaces", json={"name": "Shree Code Mantra"}, headers=headers)
    assert create_resp.status_code == 201
    workspace = create_resp.json()
    assert workspace["slug"] == "shree-code-mantra"

    list_resp = await client.get("/api/v1/workspaces", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    brand_payload = {
        "brand_name": "Shree Code Mantra",
        "industry": "Education / Technology",
        "target_audience": ["Final-year students", "Aspiring developers"],
        "brand_tone": "Friendly, expert, encouraging",
        "brand_keywords": ["Python", "FastAPI", "React", "AI", "ML"],
        "forbidden_words": ["guaranteed job"],
        "preferred_hashtags": ["#AI", "#Python", "#StudentDevelopers"],
    }
    upsert_resp = await client.put(
        f"/api/v1/workspaces/{workspace['id']}/brand", json=brand_payload, headers=headers
    )
    assert upsert_resp.status_code == 200
    brand = upsert_resp.json()
    assert brand["brand_name"] == "Shree Code Mantra"
    assert "Python" in brand["brand_keywords"]

    get_resp = await client.get(f"/api/v1/workspaces/{workspace['id']}/brand", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["industry"] == "Education / Technology"


async def test_non_member_cannot_read_brand(client):
    owner_token = await _register_and_login(client, "owner2@shreecodemantra.com")
    outsider_token = await _register_and_login(client, "outsider@shreecodemantra.com")

    create_resp = await client.post(
        "/api/v1/workspaces", json={"name": "Private Workspace"}, headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/workspaces/{workspace_id}/brand", headers={"Authorization": f"Bearer {outsider_token}"}
    )
    assert resp.status_code == 403

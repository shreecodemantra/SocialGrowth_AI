import pytest

pytestmark = pytest.mark.asyncio


async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return resp.json()["access_token"]


async def _setup_workspace_with_brand(client, email: str) -> tuple[dict, dict]:
    token = await _register_and_login(client, email)
    headers = {"Authorization": f"Bearer {token}"}

    ws_resp = await client.post("/api/v1/workspaces", json={"name": "Shree Code Mantra"}, headers=headers)
    workspace = ws_resp.json()

    brand_payload = {
        "brand_name": "Shree Code Mantra",
        "industry": "Education / Technology",
        "target_audience": ["Final-year students"],
        "brand_tone": "Friendly, expert, encouraging",
        "brand_keywords": ["Python", "FastAPI", "AI"],
        "forbidden_words": ["guaranteed job"],
        "preferred_hashtags": ["#AI", "#Python"],
    }
    await client.put(f"/api/v1/workspaces/{workspace['id']}/brand", json=brand_payload, headers=headers)

    return workspace, headers


async def test_create_campaign_requires_brand_profile(client):
    token = await _register_and_login(client, "nobrand@shreecodemantra.com")
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = await client.post("/api/v1/workspaces", json={"name": "No Brand Yet"}, headers=headers)
    workspace = ws_resp.json()

    resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "AI Projects for Students", "platforms": ["INSTAGRAM"]},
        headers=headers,
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "BRAND_PROFILE_REQUIRED"


async def test_generate_campaign_creates_post_per_platform(client):
    workspace, headers = await _setup_workspace_with_brand(client, "gen@shreecodemantra.com")

    resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={
            "title": "AI Projects for Final-Year Students",
            "goal": "Brand Awareness",
            "platforms": ["INSTAGRAM", "LINKEDIN", "YOUTUBE"],
            "generate_images": True,
        },
        headers=headers,
    )

    assert resp.status_code == 201, resp.text
    campaign = resp.json()
    assert campaign["status"] == "READY"
    assert len(campaign["posts"]) == 1

    post = campaign["posts"][0]
    assert post["display_id"].startswith("POST-")
    assert post["status"] == "PENDING_REVIEW"
    assert {p["platform"] for p in post["platforms"]} == {"INSTAGRAM", "LINKEDIN", "YOUTUBE"}

    ig = next(p for p in post["platforms"] if p["platform"] == "INSTAGRAM")
    assert set(ig["content"].keys()) >= {"caption", "hook", "cta", "hashtags", "image_prompt"}
    assert ig["status"] == "PENDING_REVIEW"
    assert ig["primary_asset"] is not None
    assert ig["primary_asset"]["storage_url"].startswith("/media/")

    li = next(p for p in post["platforms"] if p["platform"] == "LINKEDIN")
    assert set(li["content"].keys()) >= {"hook", "post", "cta", "hashtags"}

    yt = next(p for p in post["platforms"] if p["platform"] == "YOUTUBE")
    assert set(yt["content"].keys()) >= {"video_title", "description", "tags", "shorts_script"}


async def test_approval_workflow(client):
    workspace, headers = await _setup_workspace_with_brand(client, "approve@shreecodemantra.com")

    create_resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "Python Career Tips", "platforms": ["INSTAGRAM", "LINKEDIN"], "generate_images": False},
        headers=headers,
    )
    post_id = create_resp.json()["posts"][0]["id"]

    # Approve Instagram only — post should stay PENDING_REVIEW since LinkedIn isn't approved yet.
    approve_resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/INSTAGRAM/approve", headers=headers
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "APPROVED"

    post_resp = await client.get(f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}", headers=headers)
    assert post_resp.json()["status"] == "PENDING_REVIEW"

    # Approving the remaining platform should flip the whole post to APPROVED.
    await client.post(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/LINKEDIN/approve", headers=headers
    )
    post_resp = await client.get(f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}", headers=headers)
    assert post_resp.json()["status"] == "APPROVED"


async def test_reject_platform(client):
    workspace, headers = await _setup_workspace_with_brand(client, "reject@shreecodemantra.com")
    create_resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "Weekly Dev Tips", "platforms": ["FACEBOOK"], "generate_images": False},
        headers=headers,
    )
    post_id = create_resp.json()["posts"][0]["id"]

    resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/FACEBOOK/reject", headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


async def test_edit_platform_content_resets_to_pending_review(client):
    workspace, headers = await _setup_workspace_with_brand(client, "edit@shreecodemantra.com")
    create_resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "Student Success Stories", "platforms": ["FACEBOOK"], "generate_images": False},
        headers=headers,
    )
    post_id = create_resp.json()["posts"][0]["id"]

    await client.post(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/FACEBOOK/approve", headers=headers
    )

    edit_resp = await client.patch(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/FACEBOOK",
        json={"content": {"post": "Manually edited post text.", "cta": "Apply now", "hashtags": ["#dev"], "image_prompt": "x"}},
        headers=headers,
    )

    assert edit_resp.status_code == 200
    body = edit_resp.json()
    assert body["content"]["post"] == "Manually edited post text."
    assert body["status"] == "PENDING_REVIEW"  # edited content needs re-review even though it was approved


async def test_edit_platform_content_flags_forbidden_words(client):
    workspace, headers = await _setup_workspace_with_brand(client, "flag@shreecodemantra.com")
    create_resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "Career Outcomes", "platforms": ["FACEBOOK"], "generate_images": False},
        headers=headers,
    )
    post_id = create_resp.json()["posts"][0]["id"]

    edit_resp = await client.patch(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/FACEBOOK",
        json={
            "content": {
                "post": "We offer a guaranteed job to every graduate.",
                "cta": "Apply now",
                "hashtags": ["#careers"],
                "image_prompt": "x",
            }
        },
        headers=headers,
    )

    assert edit_resp.status_code == 200
    violations = edit_resp.json()["quality_violations"]
    assert any("guaranteed job" in v for v in violations)


async def test_regenerate_platform(client):
    workspace, headers = await _setup_workspace_with_brand(client, "regen@shreecodemantra.com")
    create_resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "Internship Tips", "platforms": ["LINKEDIN"], "generate_images": False},
        headers=headers,
    )
    post_id = create_resp.json()["posts"][0]["id"]

    resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/posts/{post_id}/platforms/LINKEDIN/regenerate", headers=headers
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "PENDING_REVIEW"


async def test_viewer_cannot_create_campaign(client):
    workspace, owner_headers = await _setup_workspace_with_brand(client, "owner3@shreecodemantra.com")

    viewer_token = await _register_and_login(client, "viewer@shreecodemantra.com")
    await client.post(
        f"/api/v1/workspaces/{workspace['id']}/members",
        json={"email": "viewer@shreecodemantra.com", "role": "VIEWER"},
        headers=owner_headers,
    )
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    resp = await client.post(
        f"/api/v1/workspaces/{workspace['id']}/campaigns",
        json={"title": "Should Not Be Allowed", "platforms": ["INSTAGRAM"]},
        headers=viewer_headers,
    )

    assert resp.status_code == 403

import time
import pytest
import respx
from httpx import AsyncClient, ASGITransport, Response

from app.main import app
from app.core.config import settings
from app.db.mongo_client import db_client
from app.auth.jwt_handler import decode_access_token, create_access_token
from app.routes.github_oauth_routes import (
    _store_otc,
    _consume_otc,
    _validate_state,
    _make_state,
    _otc_store,
    _otc_lock,
)

pytestmark = pytest.mark.asyncio

GITHUB_CODE = "gh-code-mock-xyz123"
GITHUB_ACCESS_TOKEN = "gho-mock-access-token-never-printed"
GITHUB_USER_ID = 99123456
GITHUB_LOGIN = "octocat-mock"
GITHUB_NAME = "Monalisa Octocat"
GITHUB_AVATAR = "https://avatars.githubusercontent.com/u/583231?v=4"
EXISTING_EMAIL = "monalisa-oauth@kritiq.io"
NEW_EMAIL = "new-github-user-noreply@kritiq.io"


def _mock_token_exchange_route():
    route = respx.post("https://github.com/login/oauth/access_token")
    route.return_value = Response(
        200,
        json={"access_token": GITHUB_ACCESS_TOKEN, "scope": "read:user,user:email,repo", "token_type": "bearer"},
    )
    return route


def _mock_token_exchange_bad_code():
    route = respx.post("https://github.com/login/oauth/access_token")
    route.return_value = Response(
        200,
        json={"error": "bad_verification_code", "error_description": "..."},
    )
    return route


def _mock_user_and_emails_route(*, email_included_in_user: bool | None = None, primary_email: str = EXISTING_EMAIL):
    user_payload = {
        "id": GITHUB_USER_ID,
        "login": GITHUB_LOGIN,
        "name": GITHUB_NAME,
        "avatar_url": GITHUB_AVATAR,
    }
    if email_included_in_user is not None:
        user_payload["email"] = primary_email if email_included_in_user else None
    user_route = respx.get("https://api.github.com/user")
    user_route.return_value = Response(200, json=user_payload)
    emails_route = respx.get("https://api.github.com/user/emails")
    emails_route.return_value = Response(
        200,
        json=[
            {"email": primary_email, "primary": True, "verified": True, "visibility": "public"},
            {"email": f"secondary-{GITHUB_LOGIN}@example.com", "primary": False, "verified": True, "visibility": None},
        ],
    )
    return user_route, emails_route


@pytest.fixture(autouse=True)
def _configured_oauth(monkeypatch):
    monkeypatch.setattr(settings, "GITHUB_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(settings, "GITHUB_CLIENT_SECRET", "test-client-secret-never-printed")
    monkeypatch.setattr(settings, "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")
    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:5173")
    monkeypatch.setattr(settings, "GITHUB_OAUTH_SCOPES", "read:user user:email repo")
    with _otc_lock:
        _otc_store.clear()


@pytest.fixture(autouse=True)
def _clean_users():
    try:
        col = db_client.get_collection("users")
        col.delete_many({"email": {"$in": [EXISTING_EMAIL, NEW_EMAIL]}})
        col.delete_many({"github_id": str(GITHUB_USER_ID)})
    except Exception:
        pass
    yield
    try:
        col = db_client.get_collection("users")
        col.delete_many({"email": {"$in": [EXISTING_EMAIL, NEW_EMAIL]}})
        col.delete_many({"github_id": str(GITHUB_USER_ID)})
    except Exception:
        pass


def _client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# 1. /auth/github redirect test
@respx.mock
async def test_github_authorize_redirects_with_state_and_scopes():
    async with _client() as ac:
        resp = await ac.get("/auth/github", follow_redirects=False)
    assert resp.status_code == 307, resp.headers
    loc = resp.headers.get("location", "")
    assert loc.startswith("https://github.com/login/oauth/authorize?"), loc
    assert "client_id=test-client-id" in loc
    assert "read%3Auser" in loc or "read:user" in loc
    assert "state=" in loc


# 2. invalid state in callback
@respx.mock
async def test_github_callback_rejects_invalid_state():
    async with _client() as ac:
        resp = await ac.get(
            f"/auth/github/callback?code={GITHUB_CODE}&state=completely-wrong-state",
            follow_redirects=False,
        )
    assert resp.status_code == 303, resp.text
    location = resp.headers.get("location", "")
    assert "github_invalid_state" in location, location


# 3. missing code in callback
@respx.mock
async def test_github_callback_rejects_missing_code():
    state = _make_state()
    async with _client() as ac:
        resp = await ac.get(
            f"/auth/github/callback?state={state}",
            follow_redirects=False,
        )
    assert resp.status_code == 303, resp.text
    assert "github_missing_code" in resp.headers.get("location", "")


# 4. access_denied error from GitHub
@respx.mock
async def test_github_callback_handles_access_denied():
    state = _make_state()
    async with _client() as ac:
        resp = await ac.get(
            f"/auth/github/callback?error=access_denied&state={state}",
            follow_redirects=False,
        )
    assert resp.status_code == 303, resp.text
    assert "github_access_denied" in resp.headers.get("location", "")


# 5. bad_verification_code from token exchange
@respx.mock
async def test_github_callback_invalid_code():
    state = _make_state()
    _mock_token_exchange_bad_code()
    async with _client() as ac:
        resp = await ac.get(
            f"/auth/github/callback?code=definitely-bad&state={state}",
            follow_redirects=False,
        )
    assert resp.status_code == 303, resp.text
    assert "github_invalid_code" in resp.headers.get("location", "")


# 6. Happy path: new GitHub user -> OTC -> frontend callback
@respx.mock
async def test_github_callback_success_new_user_exchange():
    state = _make_state()
    _mock_token_exchange_route()
    _mock_user_and_emails_route(email_included_in_user=None, primary_email=NEW_EMAIL)
    async with _client() as ac:
        callback_resp = await ac.get(
            f"/auth/github/callback?code={GITHUB_CODE}&state={state}",
            follow_redirects=False,
        )
    assert callback_resp.status_code == 303, callback_resp.text
    redirect_location = callback_resp.headers.get("location", "")
    assert redirect_location.startswith("http://localhost:5173/auth/callback"), redirect_location
    assert "otc=kr-" in redirect_location, redirect_location

    # Extract OTC from the redirect
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_location)
    otc_codes = parse_qs(parsed.query).get("otc", [])
    assert len(otc_codes) == 1, redirect_location
    otc = otc_codes[0]

    # Exchange OTC for JWT via POST /auth/github/exchange
    async with _client() as ac:
        exchange_resp = await ac.post(
            "/auth/github/exchange",
            json={"code": otc},
        )
    assert exchange_resp.status_code == 200, exchange_resp.text
    body = exchange_resp.json()
    assert body.get("token_type") == "bearer"
    jwt = body.get("access_token", "")
    assert len(jwt) > 20

    # Decode to verify the right identity is inside
    decoded = decode_access_token(jwt)
    assert decoded.get("sub") == NEW_EMAIL, decoded

    # Verify user record stored in DB
    col = db_client.get_collection("users")
    stored = col.find_one({"github_id": str(GITHUB_USER_ID)})
    assert stored is not None
    assert stored.get("github_username") == GITHUB_LOGIN
    assert stored.get("email") == NEW_EMAIL
    assert stored.get("github_access_token") == GITHUB_ACCESS_TOKEN


# 7. Existing GitHub user (github_id already in DB) — no duplicate, token refreshed
@respx.mock
async def test_github_callback_existing_user_no_duplicate():
    col = db_client.get_collection("users")
    col.insert_one({
        "github_id": str(GITHUB_USER_ID),
        "email": EXISTING_EMAIL,
        "name": "Old Name",
        "github_username": GITHUB_LOGIN,
        "github_access_token": "old-token",
        "avatar_url": None,
    })

    state = _make_state()
    _mock_token_exchange_route()
    _mock_user_and_emails_route(email_included_in_user=False, primary_email=EXISTING_EMAIL)
    async with _client() as ac:
        callback_resp = await ac.get(
            f"/auth/github/callback?code={GITHUB_CODE}&state={state}",
            follow_redirects=False,
        )
    assert callback_resp.status_code == 303
    redirect_location = callback_resp.headers.get("location", "")
    assert "otc=kr-" in redirect_location

    from urllib.parse import urlparse, parse_qs
    otc = parse_qs(urlparse(redirect_location).query).get("otc", [None])[0]

    # DB record: github_access_token REFRESHED to new value (not "old-token"),
    # and still only ONE record (no duplicate by email or github_id)
    updated = col.find_one({"github_id": str(GITHUB_USER_ID)})
    assert updated.get("github_access_token") == GITHUB_ACCESS_TOKEN
    emails = list(col.find({"email": EXISTING_EMAIL}))
    assert len(emails) == 1, "Duplicate email row created!"
    github_id_rows = list(col.find({"github_id": str(GITHUB_USER_ID)}))
    assert len(github_id_rows) == 1, "Duplicate github_id row created!"


# 8. Email-linking: Kritiq account already exists with same email; github identity gets linked
@respx.mock
async def test_github_callback_links_by_email_to_existing_account():
    col = db_client.get_collection("users")
    # Pre-existing password-registered Kritiq account (no github linkage yet)
    col.insert_one({
        "email": EXISTING_EMAIL,
        "name": "Original Name",
        "password": "bcrypt-would-be-here-normally",
    })

    state = _make_state()
    _mock_token_exchange_route()
    _mock_user_and_emails_route(email_included_in_user=True, primary_email=EXISTING_EMAIL)
    async with _client() as ac:
        callback_resp = await ac.get(
            f"/auth/github/callback?code={GITHUB_CODE}&state={state}",
            follow_redirects=False,
        )
    assert callback_resp.status_code == 303

    # Only ONE user document exists with EXISTING_EMAIL (not two rows)
    docs_with_email = list(col.find({"email": EXISTING_EMAIL}))
    assert len(docs_with_email) == 1, (
        f"Expected single document with email {EXISTING_EMAIL}, got {len(docs_with_email)}: "
        f"{docs_with_email}"
    )
    merged = docs_with_email[0]
    # Existing fields preserved
    assert merged.get("name") == "Original Name"
    assert merged.get("password") == "bcrypt-would-be-here-normally"
    # GitHub identity appended
    assert merged.get("github_id") == str(GITHUB_USER_ID)
    assert merged.get("github_username") == GITHUB_LOGIN
    assert merged.get("github_access_token") == GITHUB_ACCESS_TOKEN


# 9. OTC double-consume rejected
def test_otc_cannot_be_consumed_twice():
    code = _store_otc(EXISTING_EMAIL)
    first = _consume_otc(code)
    assert first == EXISTING_EMAIL
    second = _consume_otc(code)
    assert second is None, "OTC must be single-use"


# 10. OTC expires after TTL window (use time-travel via store purge)
def test_otc_expired_is_rejected():
    code = "kr-expired-mock"
    import time as _time
    with _otc_lock:
        _otc_store[code] = {"email": EXISTING_EMAIL, "exp": int(_time.time()) - 3600, "used": False}
    consumed = _consume_otc(code)
    assert consumed is None, "Expired OTC must be rejected"


# 11. POST /auth/github/exchange rejects junk / malformed codes
async def test_github_exchange_rejects_junk():
    async with _client() as ac:
        junk = await ac.post("/auth/github/exchange", json={"code": "kr-total-garbage-123"})
    assert junk.status_code == 400, junk.text
    assert (
        "Invalid" in junk.json().get("detail", "")
        or "expired" in junk.json().get("detail", "")
        or "already used" in junk.json().get("detail", "")
    )


# 12. GITHUB_CLIENT_ID/SECRET not configured → authorize redirects with error param
@pytest.mark.parametrize("missing", ["client_id", "client_secret", "redirect_uri"])
async def test_github_authorize_not_configured(monkeypatch, missing):
    monkeypatch.setattr(settings, "GITHUB_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(settings, "GITHUB_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setattr(settings, "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")
    if missing == "client_id":
        monkeypatch.setattr(settings, "GITHUB_CLIENT_ID", "")
    elif missing == "client_secret":
        monkeypatch.setattr(settings, "GITHUB_CLIENT_SECRET", "")
    elif missing == "redirect_uri":
        monkeypatch.setattr(settings, "GITHUB_REDIRECT_URI", "")
    async with _client() as ac:
        resp = await ac.get("/auth/github", follow_redirects=False)
    assert resp.status_code == 303, resp.text
    loc = resp.headers.get("location", "")
    assert "github_oauth_not_configured" in loc, loc


# 13. Per-user token isolation: get_user_github_token picks user's token, not global
def test_get_github_headers_per_user_overrides_shared(monkeypatch):
    from repo_integration.github_api import get_github_headers, _GLOBAL_GITHUB_TOKEN
    # User provides their own OAuth token → it must appear in Authorization header,
    # regardless of shared GITHUB_TOKEN env fallback.
    user = {"github_access_token": "gho-user-personal-token"}
    headers = get_github_headers(user)
    assert headers.get("Authorization") == "Bearer gho-user-personal-token", headers
    # Global token (if any) is not used when a per-user token exists
    no_user_headers = get_github_headers(None)
    if _GLOBAL_GITHUB_TOKEN:
        assert no_user_headers.get("Authorization") == f"Bearer {_GLOBAL_GITHUB_TOKEN}"
    else:
        assert "Authorization" not in no_user_headers


# 14. State validation round-trip
def test_state_validation():
    fresh = _make_state()
    assert _validate_state(fresh), "Freshly minted state must validate"
    # Junk state → rejected
    assert not _validate_state("totally-not-valid-base64-nonsense!!")
    # Empty / None → rejected
    assert not _validate_state("")
    assert not _validate_state(None)

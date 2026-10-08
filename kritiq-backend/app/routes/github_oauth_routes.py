import base64
import hashlib
import json
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urljoin

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.auth.jwt_handler import create_access_token, decode_token_safe, JWTError
from app.core.config import settings
from app.db.users_repo import users_repo
from app.models.user_models import GithubExchangeRequest, TokenResponse

GITHUB_WEB_BASE = "https://github.com"
GITHUB_API_BASE = "https://api.github.com"
STATE_TTL_SECONDS = 600
OTC_TTL_SECONDS = 60

_otc_lock = threading.Lock()
_otc_store: dict[str, dict[str, Any]] = {}


@dataclass
class _LoginHint:
    email: str | None = None
    display_name: str | None = None
    username: str | None = None


def _now() -> int:
    return int(time.time())


def _purge_expired_otc() -> None:
    now = _now()
    for key in list(_otc_store.keys()):
        if _otc_store[key].get("exp", 0) <= now:
            del _otc_store[key]


def _store_otc(email: str) -> str:
    code = "kr-" + secrets.token_urlsafe(32)
    with _otc_lock:
        _purge_expired_otc()
        _otc_store[code] = {"email": email, "exp": _now() + OTC_TTL_SECONDS, "used": False}
    return code


def _consume_otc(code: str) -> str | None:
    with _otc_lock:
        _purge_expired_otc()
        entry = _otc_store.get(code)
        if not entry:
            return None
        if entry.get("used", False):
            return None
        if entry.get("exp", 0) <= _now():
            del _otc_store[code]
            return None
        entry["used"] = True
        email = entry["email"]
        del _otc_store[code]
    return email


def _oauth_configured() -> bool:
    return bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET and settings.GITHUB_REDIRECT_URI)


def _make_state() -> str:
    nonce = secrets.token_urlsafe(24)
    payload = {
        "sub": "github-oauth-state",
        "nonce": nonce,
        "iat": _now(),
        "exp": _now() + STATE_TTL_SECONDS,
    }
    try:
        return create_access_token(payload, minutes=STATE_TTL_SECONDS // 60)
    except Exception:
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        import hmac
        key = (settings.JWT_SECRET or "mock-secret").encode("utf-8")
        sig = hmac.new(key, raw, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(raw + b"." + sig).decode("ascii").rstrip("=")


def _validate_state(state: str) -> bool:
    if not state:
        return False
    data = None
    try:
        decoded = decode_token_safe(state)
        if decoded and isinstance(decoded, dict) and decoded.get("sub") == "github-oauth-state":
            exp = decoded.get("exp")
            nonce = decoded.get("nonce")
            if exp and int(exp) >= _now() and nonce:
                data = decoded
    except (JWTError, ValueError, TypeError):
        data = None

    if data is None:
        try:
            padding = "=" * (-len(state) % 4)
            raw_bytes = base64.urlsafe_b64decode(state + padding)
            dot = raw_bytes.rfind(b".")
            if dot < 0:
                return False
            raw_payload = raw_bytes[:dot]
            provided_sig = raw_bytes[dot + 1:]
            import hmac
            key = (settings.JWT_SECRET or "mock-secret").encode("utf-8")
            expected = hmac.new(key, raw_payload, hashlib.sha256).digest()
            if not hmac.compare_digest(expected, provided_sig):
                return False
            obj = json.loads(raw_payload.decode("utf-8"))
            if obj.get("sub") != "github-oauth-state":
                return False
            if int(obj.get("exp", 0)) < _now():
                return False
            if not obj.get("nonce"):
                return False
        except Exception:
            return False
    return True


def _frontend_error_redirect(reason: str) -> RedirectResponse:
    base = settings.FRONTEND_URL.rstrip("/")
    url = f"{base}/login?error={reason}"
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


def _frontend_success_redirect(otc: str) -> RedirectResponse:
    base = settings.FRONTEND_URL.rstrip("/")
    url = f"{base}/auth/callback?otc={otc}"
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


async def _exchange_code_for_token(code: str) -> tuple[str | None, str | None]:
    if not _oauth_configured():
        return None, "github_oauth_not_configured"
    token_url = f"{GITHUB_WEB_BASE}/login/oauth/access_token"
    payload = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            resp = await client.post(
                token_url,
                json=payload,
                headers={"Accept": "application/json"},
            )
    except httpx.HTTPError:
        return None, "github_network_error"

    if resp.status_code != 200:
        return None, "github_code_exchange_failed"

    try:
        body = resp.json()
    except ValueError:
        return None, "github_code_exchange_failed"

    if not isinstance(body, dict):
        return None, "github_code_exchange_failed"
    if "error" in body:
        err = body.get("error")
        if err == "bad_verification_code":
            return None, "github_invalid_code"
        if err == "redirect_uri_mismatch":
            return None, "github_redirect_uri_mismatch"
        return None, "github_oauth_error"
    access_token = body.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        return None, "github_oauth_error"
    return access_token, None


async def _fetch_github_user_and_email(access_token: str) -> tuple[dict | None, _LoginHint | None, str | None]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            user_resp = await client.get(f"{GITHUB_API_BASE}/user", headers=headers)
            if user_resp.status_code != 200:
                return None, None, "github_api_failed"
            user_obj = user_resp.json()
            if not isinstance(user_obj, dict):
                return None, None, "github_api_failed"

            email = None
            provided = user_obj.get("email")
            if isinstance(provided, str) and provided:
                email = provided
            else:
                emails_resp = await client.get(f"{GITHUB_API_BASE}/user/emails", headers=headers)
                if emails_resp.status_code == 200:
                    emails = emails_resp.json()
                    if isinstance(emails, list):
                        primary = next(
                            (e for e in emails if isinstance(e, dict) and e.get("primary") and e.get("verified")),
                            None,
                        )
                        if primary and isinstance(primary.get("email"), str):
                            email = primary["email"]
                        else:
                            first_verified = next(
                                (e for e in emails if isinstance(e, dict) and e.get("verified")),
                                None,
                            )
                            if first_verified and isinstance(first_verified.get("email"), str):
                                email = first_verified["email"]
                            elif emails and isinstance(emails[0], dict) and isinstance(emails[0].get("email"), str):
                                email = emails[0]["email"]
    except httpx.HTTPError:
        return None, None, "github_network_error"

    github_id = user_obj.get("id")
    if github_id is None:
        return None, None, "github_api_failed"

    hint = _LoginHint(
        email=email,
        display_name=user_obj.get("name") or user_obj.get("login"),
        username=user_obj.get("login"),
    )
    return user_obj, hint, None


router = APIRouter()


@router.get(
    "/github",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Initiate GitHub OAuth authorization flow",
    description=(
        "Redirects the caller to GitHub's OAuth authorization page with a signed, "
        "expiring state token for CSRF protection and the minimum required scopes "
        "(read:user, user:email, repo) so the caller can later review private repos."
    ),
    responses={
        307: {"description": "Temporary redirect to GitHub /login/oauth/authorize"},
        503: {"description": "GitHub OAuth environment variables are not configured."},
    },
)
async def github_authorize():
    if not _oauth_configured():
        return _frontend_error_redirect("github_oauth_not_configured")

    state = _make_state()
    authorize_url = f"{GITHUB_WEB_BASE}/login/oauth/authorize"
    query = urlencode({
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": settings.GITHUB_OAUTH_SCOPES,
        "state": state,
        "allow_signup": "true",
    })
    return RedirectResponse(url=f"{authorize_url}?{query}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get(
    "/github/callback",
    status_code=status.HTTP_303_SEE_OTHER,
    summary="GitHub OAuth callback — exchange code for session and redirect to dashboard",
    description=(
        "Validates the signed state parameter, exchanges the GitHub authorization code "
        "for a GitHub access token, loads the GitHub user's identity and email, links "
        "or creates a Kritiq user, stores the GitHub access token server-side, and "
        "finally redirects to the frontend with a single-use handoff code which the "
        "frontend exchanges for a Kritiq JWT. All sensitive tokens stay server-side."
    ),
)
async def github_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    if not _oauth_configured():
        return _frontend_error_redirect("github_oauth_not_configured")

    if error:
        if error == "access_denied":
            return _frontend_error_redirect("github_access_denied")
        return _frontend_error_redirect("github_oauth_error")

    if not code:
        return _frontend_error_redirect("github_missing_code")

    if not _validate_state(state):
        return _frontend_error_redirect("github_invalid_state")

    access_token, err = await _exchange_code_for_token(code)
    if access_token is None:
        return _frontend_error_redirect(err or "github_oauth_error")

    user_obj, login_hint, err = await _fetch_github_user_and_email(access_token)
    if user_obj is None or login_hint is None:
        return _frontend_error_redirect(err or "github_api_failed")

    github_id = str(user_obj["id"])
    username = login_hint.username or ""
    avatar_url = user_obj.get("avatar_url") if isinstance(user_obj.get("avatar_url"), str) else None

    email = login_hint.email
    if not email:
        email = f"github-{github_id}@users.noreply.github.com"

    display_name = login_hint.display_name or username or "GitHub User"

    user_record = await users_repo.upsert_github_user(
        github_id=github_id,
        email=email,
        name=display_name,
        github_username=username,
        github_access_token=access_token,
        avatar_url=avatar_url,
    )

    if not user_record or not user_record.get("email"):
        return _frontend_error_redirect("account_linking_failed")

    otc = _store_otc(user_record["email"])
    return _frontend_success_redirect(otc)


@router.post(
    "/github/exchange",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange a single-use handoff code for a Kritiq JWT session",
    description=(
        "Used by the frontend after the GitHub OAuth callback redirects the user to "
        "/auth/callback?otc=.... The OTC is valid for 60 seconds, single-use, and "
        "cannot be replayed. On success the client receives a standard Kritiq Bearer "
        "JWT identical to the one issued by POST /auth/login and /auth/register."
    ),
    responses={
        200: {"description": "OTC valid, Kritiq JWT session issued."},
        400: {"description": "OTC missing, expired, already used, or unknown."},
    },
)
async def github_exchange_otc(payload: GithubExchangeRequest):
    email = _consume_otc(payload.code)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already used handoff code.",
        )
    user = await users_repo.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Linked account no longer exists.",
        )
    jwt = create_access_token(data={"sub": email})
    return {"access_token": jwt, "token_type": "bearer"}

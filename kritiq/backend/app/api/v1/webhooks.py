"""
GitHub webhook receiver — validates HMAC-SHA256 signatures and enqueues
pipeline runs.

Endpoint: POST /webhook/github
  • 401  — invalid / missing signature
  • 202  — accepted, pipeline queued (stub for now)
"""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request, BackgroundTasks

from app.core.config import settings
from app.schemas.webhook import WebhookEvent, WebhookPayload

logger = logging.getLogger("kritiq.webhooks")

router = APIRouter(prefix="/webhook", tags=["Webhooks"])


# ── Helpers ──────────────────────────────────────────────

def _verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verify the request body against the ``X-Hub-Signature-256`` header.

    GitHub sends ``sha256=<hex-digest>``; we recompute the HMAC with
    our shared secret and compare in constant time.
    """
    expected = "sha256=" + hmac.new(
        key=settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def _extract_payload(event_type: str, data: dict) -> WebhookPayload:
    """
    Pull the three fields KRITIQ needs out of the raw GitHub JSON,
    which differs between ``push`` and ``pull_request`` events.
    """
    repo = data.get("repository", {})
    repo_url = repo.get("html_url", repo.get("url", ""))

    if event_type == "push":
        head = data.get("head_commit", {})
        commit_sha = head.get("id", "")
    else:  # pull_request
        pr = data.get("pull_request", {})
        commit_sha = pr.get("head", {}).get("sha", "")

    # live_url is not part of the standard GitHub payload — it can be
    # injected via a custom property on the repo or sent separately.
    live_url = data.get("live_url") or repo.get("homepage") or None

    return WebhookPayload(
        repo_url=repo_url,
        commit_sha=commit_sha,
        live_url=live_url,
    )


# ── Route ────────────────────────────────────────────────

@router.post("/github", status_code=202)
async def receive_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(
        ..., alias="X-Hub-Signature-256",
        description="HMAC-SHA256 signature sent by GitHub",
    ),
    x_github_event: str = Header(
        ..., alias="X-GitHub-Event",
        description="push | pull_request",
    ),
):
    """
    Receive a GitHub webhook, verify its HMAC-SHA256 signature,
    parse the payload, and hand it off to the review pipeline.

    Returns **202 Accepted** on success so GitHub doesn't wait for the
    full pipeline to finish.
    """
    raw_body = await request.body()

    # ── 1. Signature verification ────────────────────────
    if not _verify_signature(raw_body, x_hub_signature_256):
        logger.warning("Rejected webhook — invalid HMAC signature")
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    # ── 2. Parse payload ─────────────────────────────────
    data: dict = await request.json()
    payload = _extract_payload(x_github_event, data)

    event = WebhookEvent(event_type=x_github_event, payload=payload)

    logger.info(
        "Webhook accepted  repo=%s  sha=%s  event=%s",
        payload.repo_url,
        payload.commit_sha[:8],
        event.event_type,
    )

    # ── 3. Queue pipeline run in background ──────────────────
    from app.core.orchestrator import run_pipeline
    background_tasks.add_task(run_pipeline, payload)

    return {
        "message": "Webhook received — pipeline queued",
        "event_type": event.event_type,
        "repo_url": payload.repo_url,
        "commit_sha": payload.commit_sha,
    }

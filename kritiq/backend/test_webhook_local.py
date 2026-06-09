"""
test_webhook_local.py — Send a fake GitHub push webhook to the local server.

Usage:
    python test_webhook_local.py [--url URL] [--secret SECRET]

The script:
  1. Builds a minimal GitHub-like push payload
  2. Computes the correct HMAC-SHA256 signature
  3. POSTs it to the local /webhook/github endpoint
  4. Prints the response

This is handy for smoke-testing before you wire up ngrok + GitHub.
"""

import argparse
import hashlib
import hmac
import json
import sys

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a test webhook to KRITIQ")
    parser.add_argument(
        "--url",
        default="http://localhost:8000/webhook/github",
        help="Webhook endpoint URL",
    )
    parser.add_argument(
        "--secret",
        default="your_webhook_secret_here",
        help="GITHUB_WEBHOOK_SECRET value (must match the server)",
    )
    args = parser.parse_args()

    # ── Build a fake GitHub push payload ─────────────────
    payload = {
        "ref": "refs/heads/main",
        "head_commit": {
            "id": "abc123def456789",
            "message": "fix: patch security hole in auth module",
        },
        "repository": {
            "name": "my-repo",
            "html_url": "https://github.com/octocat/my-repo",
            "url": "https://api.github.com/repos/octocat/my-repo",
            "clone_url": "https://github.com/octocat/my-repo.git",
            "homepage": "https://my-repo.vercel.app",
            "owner": {"login": "octocat"},
        },
    }

    body = json.dumps(payload, separators=(",", ":")).encode()

    # ── Compute HMAC-SHA256 signature ────────────────────
    signature = "sha256=" + hmac.new(
        key=args.secret.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": signature,
    }

    # ── Fire! ────────────────────────────────────────────
    print(f"→  POST {args.url}")
    print(f"   X-Hub-Signature-256: {signature[:30]}…")

    resp = httpx.post(args.url, content=body, headers=headers)

    print(f"←  {resp.status_code}  {resp.text}")

    # ── Test with bad signature ──────────────────────────
    print("\n→  Sending INVALID signature…")
    headers["X-Hub-Signature-256"] = "sha256=bad_signature_value"
    resp_bad = httpx.post(args.url, content=body, headers=headers)
    print(f"←  {resp_bad.status_code}  {resp_bad.text}")

    if resp.status_code == 202 and resp_bad.status_code == 401:
        print("\n✅  Both tests passed!")
    else:
        print("\n❌  Something unexpected happened — review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

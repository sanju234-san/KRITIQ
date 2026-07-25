"""Verify the new CORS allowlist works for the user's new origin + random preview + local ports."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

CASES = [
    ("New blocked production",   "https://kritiq-navy.vercel.app"),
    ("Old production",           "https://kritiq-git-main-sanju234-sans-projects.vercel.app"),
    ("Random Vercel preview 1",  "https://kritiq-fix-login-abc123-sans-projects.vercel.app"),
    ("Random Vercel preview 2",  "https://kritiq-pr-42.vercel.app"),
    ("Localhost :5173",          "http://localhost:5173"),
    ("Localhost :3000",          "http://localhost:3000"),
    ("Localhost :5174",          "http://localhost:5174"),
    ("127.0.0.1 :8000",          "http://127.0.0.1:8000"),
    ("Malicious origin should FAIL", "https://evil.com"),
]

PREFLIGHT_HEADERS = {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type,authorization",
}

FAIL = []
for label, origin in CASES:
    print()
    print("=" * 80)
    print(f"[{label}]  Origin = {origin}")
    headers = dict(PREFLIGHT_HEADERS)
    headers["Origin"] = origin
    resp = client.options("/auth/login", headers=headers)
    print(f"< HTTP {resp.status_code}")
    acao = resp.headers.get("Access-Control-Allow-Origin")
    acac = resp.headers.get("Access-Control-Allow-Credentials")
    print(f"< Access-Control-Allow-Origin     : {acao!r}")
    print(f"< Access-Control-Allow-Credentials: {acac!r}")

    expect_pass = not label.startswith("Malicious")
    if expect_pass:
        if acao == origin and resp.status_code == 200:
            print(f"  OK: Origin allowed.")
        else:
            s = f"FAIL: Origin {origin} was NOT allowed (status={resp.status_code}, ACAO={acao!r})"
            print(f"  {s}")
            FAIL.append(s)
    else:
        # Evil origin: expect either no ACAO OR the echo is wrong
        if acao == origin:
            s = f"SECURITY FAIL: Malicious origin {origin} was allowed!"
            print(f"  {s}")
            FAIL.append(s)
        else:
            print(f"  OK: Malicious origin correctly blocked (ACAO={acao!r}).")

# Also verify real POST login still works for the newly-allowed origin
print()
print("=" * 80)
print("[REAL POST LOGIN]  with Origin = https://kritiq-navy.vercel.app")
r = client.post(
    "/auth/login",
    headers={"Origin": "https://kritiq-navy.vercel.app", "Content-Type": "application/json"},
    json={"email": "github_dev@kritiq.io", "password": "githubdevpwd123"},
)
print(f"< HTTP {r.status_code}")
print(f"< ACAO = {r.headers.get('Access-Control-Allow-Origin')!r}")
print(f"< ACAC = {r.headers.get('Access-Control-Allow-Credentials')!r}")
body_text = r.text
print(f"< Body (truncated): {body_text[:200]}")
if r.headers.get("Access-Control-Allow-Origin") != "https://kritiq-navy.vercel.app":
    FAIL.append("POST /auth/login for new navy origin missing ACAO header")
if r.status_code != 200:
    FAIL.append(f"POST /auth/login for new navy origin returned {r.status_code}, expected 200")

print()
print("=" * 80)
if FAIL:
    print(f"FAILED CHECKS ({len(FAIL)}):")
    for f in FAIL:
        print("  - " + f)
    raise SystemExit(1)
else:
    print("[PASS] All CORS origin checks passed.")

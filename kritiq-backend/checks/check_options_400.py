"""Reproduce the 400 Bad Request on OPTIONS preflight for /auth/login and /auth/register."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ORIGIN = "http://localhost:5173"

def run(method, path, headers=None, expected_status_set=None):
    print("=" * 80)
    print(f"> {method} {path}")
    if headers:
        for k, v in headers.items():
            print(f"> {k}: {v}")
    resp = client.request(method, path, headers=headers or {})
    print(f"< HTTP {resp.status_code} {resp.reason_phrase}")
    for k, v in resp.headers.items():
        print(f"< {k}: {v}")
    text = resp.text
    if text:
        print(f"\n<Body>: {text[:500]}")
    if expected_status_set and resp.status_code not in expected_status_set:
        print(f"\n!!! FAIL: expected one of {expected_status_set}, got {resp.status_code}")
    return resp

# 1) Bare OPTIONS /auth/login (no CORS headers) — will it be 400?
run("OPTIONS", "/auth/login", expected_status_set={200, 204})

# 2) OPTIONS /auth/login with preflight headers (how browser sends it)
run("OPTIONS", "/auth/login", headers={
    "Origin": ORIGIN,
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type,authorization",
}, expected_status_set={200, 204})

# 3) Same for /auth/register
run("OPTIONS", "/auth/register", headers={
    "Origin": ORIGIN,
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type,authorization",
}, expected_status_set={200, 204})

# 4) Sanity check: GET / (should be 200)
run("GET", "/", expected_status_set={200})

# 5) Sanity check: GET /history/ (should be 401 because no JWT, not 400/405)
run("GET", "/history/", headers={"Origin": ORIGIN}, expected_status_set={401, 200})

# 6) Bare POST /auth/login (should be 422 missing body, not 400)
run("POST", "/auth/login", headers={"Content-Type": "application/json", "Origin": ORIGIN}, expected_status_set={422})

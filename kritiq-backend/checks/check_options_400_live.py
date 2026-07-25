"""
Replay the exact Render log scenario: try different OPTIONS permutations against the LIVE backend
to figure out what triggers 400 (not 405, not 200). The Render log shows:
  OPTIONS /auth/login -> 400 Bad Request
  OPTIONS /auth/register -> 400 Bad Request
but
  GET /history/ -> 200 OK

Also test trailing slash variants because /auth/login vs /auth/login/ can behave differently.
"""
import requests
import sys

BACKEND = "https://kritiq.onrender.com"
LIVE_VERCEL_ORIGIN = "https://kritiq-git-main-sanju234-sans-projects.vercel.app"

# These are the exact combos a browser / axios could reasonably send.
CASES = [
    ("OPTIONS", "/auth/login", {"Origin": LIVE_VERCEL_ORIGIN, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type,authorization"}),
    ("OPTIONS", "/auth/login/", {"Origin": LIVE_VERCEL_ORIGIN, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type,authorization"}),
    ("OPTIONS", "/auth/register", {"Origin": LIVE_VERCEL_ORIGIN, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type,authorization"}),
    ("OPTIONS", "/auth/register/", {"Origin": LIVE_VERCEL_ORIGIN, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type,authorization"}),

    # Missing Access-Control-Request-Method (malformed preflight that CORS middleware might
    # fall through and leave to the router, which does not register OPTIONS handler -> behavior
    # depends on 404/405 handler path)
    ("OPTIONS", "/auth/login", {"Origin": LIVE_VERCEL_ORIGIN}),

    # Plain OPTIONS no Origin
    ("OPTIONS", "/auth/login", {}),

    # Control: real POST login request
    ("POST", "/auth/login", {"Origin": LIVE_VERCEL_ORIGIN, "Content-Type": "application/json"}, {"email": "github_dev@kritiq.io", "password": "githubdevpwd123"}),
]

s = requests.Session()
FAIL = []
for i, case in enumerate(CASES):
    method, path, headers, *rest = case
    json = rest[0] if rest else None
    print()
    print("=" * 80)
    print(f"Case {i+1}: {method} {path}")
    for k, v in headers.items():
        print(f"> {k}: {v}")
    if json:
        print(f"> JSON: {json}")
    try:
        resp = s.request(method, BACKEND + path, headers=headers, json=json, timeout=30)
    except requests.RequestException as e:
        print(f"!! Network error: {e}")
        FAIL.append(f"Case {i+1}: network")
        continue
    print(f"< HTTP {resp.status_code} {resp.reason}")
    for k, v in resp.headers.items():
        if k.lower().startswith("access-control-") or k.lower() in ("content-length", "content-type", "vary", "allow"):
            print(f"< {k}: {v}")
    body = resp.text
    if body:
        preview = body[:300]
        print(f"<Body>: {preview}")
    if resp.status_code == 400:
        FAIL.append(f"Case {i+1}: {method} {path} returned 400 — THIS MATCHES THE RENDER LOG")
    print()
print("=" * 80)
if FAIL:
    print("FAILURES:")
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
else:
    print("[PASS] None of the cases produced a 400 Bad Request.")

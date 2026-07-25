"""
Reproduce the user's exact CORS failure: origin https://kritiq-navy.vercel.app is blocked because
it's not in the current allow_origins list of the live Render backend.
"""
import requests

BACKEND = "https://kritiq.onrender.com"
BLOCKED_ORIGIN = "https://kritiq-navy.vercel.app"
PREVIOUS_ORIGIN = "https://kritiq-git-main-sanju234-sans-projects.vercel.app"

def run(label, origin):
    print()
    print("=" * 80)
    print(f"CASE: {label}")
    print(f"> Origin: {origin}")
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,authorization",
    }
    resp = requests.options(BACKEND + "/auth/login", headers=headers, timeout=30)
    print(f"< HTTP {resp.status_code} {resp.reason}")
    acao = resp.headers.get("Access-Control-Allow-Origin")
    acac = resp.headers.get("Access-Control-Allow-Credentials")
    print(f"< Access-Control-Allow-Origin     : {acao!r}")
    print(f"< Access-Control-Allow-Credentials: {acac!r}")
    if resp.text:
        print(f"< Body: {resp.text[:200]}")
    if acao is None or acao != origin:
        print("  !!! BLOCKED: No matching ACAO header. Browser will reject with CORS error.")
        return False
    print("  OK: CORS preflight passed for this origin.")
    return True

ok1 = run("BLOCKED NEW ORIGIN (user's actual error)", BLOCKED_ORIGIN)
ok2 = run("OLD PREVIOUS Vercel origin (was previously working)", PREVIOUS_ORIGIN)
ok3 = run("Localhost dev origin", "http://localhost:5173")

print()
print("=" * 80)
if not ok1:
    print(f"[CONFIRMED ROOT CAUSE] Origin {BLOCKED_ORIGIN} is NOT present in Render's allow_origins list.")
    print(f"The backend only allows: FRONTEND_URL env var + hardcoded localhost:5173.")

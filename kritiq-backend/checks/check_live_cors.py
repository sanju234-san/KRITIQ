"""
Live CORS test against https://kritiq.onrender.com for the Vercel Origin:
  Origin: https://kritiq-git-main-sanju234-sans-projects.vercel.app

Runs:
  A) GET / with Origin -> verify Access-Control-Allow-Origin
  B) OPTIONS preflight to /auth/login
  C) POST /auth/login with Origin (valid demo credentials)
  D) GET /auth/profile with Bearer token + Origin
"""
import requests
import json
import sys

BACKEND = "https://kritiq.onrender.com"
ORIGIN = "https://kritiq-git-main-sanju234-sans-projects.vercel.app"
PREFLIGHT_URL = BACKEND + "/auth/login"

DEMO_EMAIL = "github_dev@kritiq.io"
DEMO_PASSWORD = "githubdevpwd123"

session = requests.Session()
FAIL = []

def hr(title):
    print("")
    print("=" * 80)
    print("  " + title)
    print("=" * 80)

def print_req(method, url, req_headers, title):
    hr(title)
    print("> " + method + " " + url)
    for k, v in req_headers.items():
        print("> " + k + ": " + v)

def print_resp(resp, body_preview=True, max_body_chars=600):
    print("< HTTP " + str(resp.status_code) + " " + str(resp.reason))
    for k, v in resp.headers.items():
        print("< " + k + ": " + v)
    if body_preview:
        text = resp.text
        if len(text) > max_body_chars:
            text = text[:max_body_chars] + "... (truncated, " + str(len(resp.text)) + " bytes total)"
        print("")
        print("<body>: " + text)

def check_header(name, expected_value_or_contains=None, contains=False, required=True):
    # 'resp' is assigned in outer scope just before each call
    val = resp.headers.get(name)
    status = ""
    if val is None:
        if required:
            status = "[FAIL] MISSING required header '" + name + "'"
            FAIL.append(status)
        else:
            status = "[INFO] Header '" + name + "' absent (optional)"
    else:
        if expected_value_or_contains is None:
            status = "[PASS] '" + name + "': " + val
        elif contains:
            if expected_value_or_contains.lower() in val.lower():
                status = "[PASS] '" + name + "' contains '" + expected_value_or_contains + "': " + val
            else:
                status = "[FAIL] '" + name + "' did NOT contain '" + expected_value_or_contains + "': " + val
                FAIL.append(status)
        else:
            if val == expected_value_or_contains:
                status = "[PASS] '" + name + "' == expected: " + val
            else:
                status = "[FAIL] '" + name + "' mismatch. Expected '" + expected_value_or_contains + "', got '" + val + "'"
                FAIL.append(status)
    print("   -> " + status)
    return val

# -----------------------------------------------------------------------------
# STEP 1b: GET / with Origin -> verify ACAO header matches Vercel URL
# -----------------------------------------------------------------------------
req_headers = {"Origin": ORIGIN}
print_req("GET", BACKEND + "/", req_headers,
          "STEP 1b: GET root with Vercel Origin -> verify Access-Control-Allow-Origin")
try:
    resp = session.get(BACKEND + "/", headers=req_headers, timeout=30)
except requests.exceptions.RequestException as e:
    print("")
    print("[FATAL] Network error: " + str(e))
    sys.exit(1)
print_resp(resp)
acao = check_header("Access-Control-Allow-Origin", ORIGIN)
check_header("Access-Control-Allow-Credentials", "true")

# -----------------------------------------------------------------------------
# STEP 2a: OPTIONS preflight
# -----------------------------------------------------------------------------
preflight_headers = {
    "Origin": ORIGIN,
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type,authorization",
}
print_req("OPTIONS", PREFLIGHT_URL, preflight_headers,
          "STEP 2a: OPTIONS Preflight to /auth/login")
resp = session.options(PREFLIGHT_URL, headers=preflight_headers, timeout=30)
print_resp(resp)
if resp.status_code not in (200, 204):
    s = "[FAIL] Preflight status " + str(resp.status_code) + " not 200/204"
    print(s)
    FAIL.append(s)
else:
    print("[PASS] Preflight returned HTTP " + str(resp.status_code))
check_header("Access-Control-Allow-Origin", ORIGIN)
check_header("Access-Control-Allow-Methods", "POST", contains=True)
check_header("Access-Control-Allow-Credentials", "true")
check_header("Access-Control-Allow-Headers", "content-type", contains=True, required=False)

# -----------------------------------------------------------------------------
# STEP 2b: Actual POST /auth/login with Origin (demo credentials)
# -----------------------------------------------------------------------------
actual_headers = {
    "Origin": ORIGIN,
    "Content-Type": "application/json",
}
payload = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
print_req("POST", BACKEND + "/auth/login", actual_headers,
          "STEP 2b: Actual POST /auth/login with Vercel Origin + demo credentials")
resp = session.post(BACKEND + "/auth/login", headers=actual_headers, json=payload, timeout=30)
print_resp(resp, max_body_chars=400)
token = None
if resp.status_code != 200:
    s = "[FAIL] Login returned " + str(resp.status_code) + ", expected 200"
    print(s)
    FAIL.append(s)
else:
    print("[PASS] Login returned HTTP 200")
try:
    body = resp.json()
    token = body.get("access_token")
    if token:
        print("[PASS] access_token present (len=" + str(len(token)) + ")")
    else:
        s = "[FAIL] access_token missing in login response"
        print(s)
        FAIL.append(s)
except Exception:
    s = "[FAIL] Login response was not JSON"
    print(s)
    FAIL.append(s)
check_header("Access-Control-Allow-Origin", ORIGIN)
check_header("Access-Control-Allow-Credentials", "true")

# -----------------------------------------------------------------------------
# STEP 2c: GET /auth/profile with Bearer token + Origin (cross-origin authed request)
# -----------------------------------------------------------------------------
if token:
    authed_headers = {
        "Origin": ORIGIN,
        "Authorization": "Bearer " + token,
    }
    print_req("GET", BACKEND + "/auth/profile", authed_headers,
              "STEP 2c: Cross-origin authed GET /auth/profile")
    resp = session.get(BACKEND + "/auth/profile", headers=authed_headers, timeout=30)
    print_resp(resp, max_body_chars=500)
    if resp.status_code == 200:
        try:
            b = resp.json()
            if b.get("email") == DEMO_EMAIL.lower() and b.get("name") == "GitHub Developer":
                print("[PASS] Profile matches expected: " + str(b.get("name")) + " / " + str(b.get("email")))
            else:
                s = "[WARN] Profile unexpected: " + json.dumps(b)
                print(s)
                FAIL.append(s)
        except Exception:
            FAIL.append("[FAIL] Profile response not JSON")
    else:
        s = "[FAIL] /auth/profile returned HTTP " + str(resp.status_code) + " - cross-origin auth broken"
        print(s)
        FAIL.append(s)
    check_header("Access-Control-Allow-Origin", ORIGIN)
    check_header("Access-Control-Allow-Credentials", "true")

# -----------------------------------------------------------------------------
# FINAL SUMMARY
# -----------------------------------------------------------------------------
hr("SUMMARY")
if FAIL:
    print("FAILED checks (" + str(len(FAIL)) + "):")
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
else:
    print("[PASS] ALL CORS / cross-origin auth header checks PASSED against live Render backend + Vercel Origin.")

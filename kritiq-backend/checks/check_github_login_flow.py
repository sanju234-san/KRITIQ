"""
LIVE end-to-end test replicating the frontend handleGithubLogin flow:
  1. POST /auth/login with demo GitHub creds -> expect 401 (user doesn't exist yet)
  2. POST /auth/register with ('GitHub Developer', github_dev@kritiq.io, githubdevpwd123) -> expect 200 + token
  3. GET /auth/profile with the register-returned token -> expect 200 + profile
  4. POST /auth/login again with same creds -> expect 200 + new token
  5. GET /auth/profile with login token -> expect 200 + profile

This matches exactly what Login.jsx handleGithubLogin() does.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

DEMO_EMAIL = "github_dev@kritiq.io"
DEMO_PASSWORD = "githubdevpwd123"
DEMO_NAME = "GitHub Developer"

def log(step, msg):
    print(f"\n[{step}] {'='*50}")
    print(msg)

# ---------- STEP 1: Attempt login first (should fail, user not registered) ----------
log("STEP 1", "POST /auth/login — expect 401 because user does not yet exist")
r1 = client.post(
    "/auth/login",
    json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
)
print(f"Status: {r1.status_code}")
body1 = r1.json()
print(f"Body:   {body1}")
user_exists_from_prev_run = False
if r1.status_code == 200:
    user_exists_from_prev_run = True
    print("INFO: User already existed in DB (from previous run). Login succeeded immediately — this is the 2nd+ invocation path.")
    existing_login_token = body1.get("access_token")
else:
    assert r1.status_code == 401, f"Expected 401 on brand-new first login attempt, got {r1.status_code}"
    print("PASS: Got expected 401 Unauthorized (brand-new user, not yet registered)")

# ---------- STEP 2: Register the demo GitHub user ----------
log("STEP 2", f"POST /auth/register — create user '{DEMO_NAME}'")
r2 = client.post(
    "/auth/register",
    json={
        "name": DEMO_NAME,
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    }
)
print(f"Status: {r2.status_code}")
body2 = r2.json()
if r2.status_code == 200:
    print(f"access_token: {body2.get('access_token','')[:40]}...")
    print(f"token_type:   {body2.get('token_type')}")
elif r2.status_code == 400 and "already registered" in str(body2.get("detail", "")).lower():
    print(f"Note: User already exists ({body2}) — proceeding to re-login.")
else:
    print(f"Body: {body2}")
assert r2.status_code in (200, 400), f"Expected 200 or 400(duplicate), got {r2.status_code}"

# If duplicate, register won't return a token — we'll rely on login from Step 4.
register_token = body2.get("access_token") if r2.status_code == 200 else None

# ---------- STEP 3: /auth/profile with register-returned token (if any) ----------
if user_exists_from_prev_run:
    log("STEP 3", "GET /auth/profile using token from the successful login in STEP 1")
    r3 = client.get(
        "/auth/profile",
        headers={"Authorization": f"Bearer {existing_login_token}"}
    )
    print(f"Status: {r3.status_code}")
    body3 = r3.json()
    if r3.status_code == 200:
        print(f"Profile: id={body3.get('id')[:12]}... name={body3.get('name')} email={body3.get('email')}")
    else:
        print(f"Body: {body3}")
    assert r3.status_code == 200, f"/profile after step-1 login failed with {r3.status_code}: {body3}"
    assert body3["email"] == DEMO_EMAIL.lower(), "profile email mismatch"
    assert body3["name"] == DEMO_NAME, f"profile name mismatch: got '{body3.get('name')}' vs expected '{DEMO_NAME}'"
    print("PASS: Step-1 login token works for /profile, name & email match")
elif register_token:
    log("STEP 3", "GET /auth/profile using token from /register")
    r3 = client.get(
        "/auth/profile",
        headers={"Authorization": f"Bearer {register_token}"}
    )
    print(f"Status: {r3.status_code}")
    body3 = r3.json()
    if r3.status_code == 200:
        print(f"Profile: id={body3.get('id')[:12]}... name={body3.get('name')} email={body3.get('email')}")
    else:
        print(f"Body: {body3}")
    assert r3.status_code == 200, f"/profile after register failed with {r3.status_code}: {body3}"
    assert body3["email"] == DEMO_EMAIL.lower(), "profile email mismatch"
    assert body3["name"] == DEMO_NAME, "profile name mismatch"
    print("PASS: Register token works for /profile, name & email match")
else:
    log("STEP 3", "SKIP — user was already registered, no token from step 2.")

# ---------- STEP 4: Login again ----------
log("STEP 4", "POST /auth/login — now the user exists, expect 200")
r4 = client.post(
    "/auth/login",
    json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
)
print(f"Status: {r4.status_code}")
body4 = r4.json()
print(f"Body access_token (truncated): {body4.get('access_token','')[:40]}...")
assert r4.status_code == 200, f"Login failed after register: {r4.status_code} {body4}"
login_token = body4["access_token"]
assert login_token, "No access_token in login response"
print("PASS: Login successful")

# ---------- STEP 5: /auth/profile with login token ----------
log("STEP 5", "GET /auth/profile using token from /login")
r5 = client.get(
    "/auth/profile",
    headers={"Authorization": f"Bearer {login_token}"}
)
print(f"Status: {r5.status_code}")
body5 = r5.json()
if r5.status_code == 200:
    print(f"Profile: id={body5.get('id')[:12]}... name={body5.get('name')} email={body5.get('email')}")
else:
    print(f"Body: {body5}")
assert r5.status_code == 200, f"/profile after login failed with {r5.status_code}: {body5}"
assert body5["email"] == DEMO_EMAIL.lower()
assert body5["name"] == DEMO_NAME
print("PASS: Login token works for /profile")

print("\n" + "=" * 60)
print("ALL STEPS PASSED: handleGithubLogin flow is working end-to-end.")
print("=" * 60)

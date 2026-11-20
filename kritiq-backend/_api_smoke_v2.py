import httpx
import sys

BASE = "http://localhost:8000"

def test(name, method, path, **kwargs):
    try:
        r = httpx.request(method, f"{BASE}{path}", timeout=10, **kwargs)
        print(f"[{r.status_code}] {method} {path} — {name}")
        if r.status_code >= 400:
            try:
                data = r.json()
                print(f"    detail: {data.get('detail', data)}")
            except Exception:
                print(f"    body: {r.text[:200]}")
        return r
    except Exception as e:
        print(f"[ERR] {method} {path} — {name}: {e}")
        return None

# 1. Root/health
r = test("Health root", "GET", "/")

# 2. OPTIONS catch-all (CORS preflight)
r = test("OPTIONS catch-all", "OPTIONS", "/auth/login")

# 3. Protected endpoint (no token) - EXPECT 401
r = test("Protected /auth/profile no token", "GET", "/auth/profile")

# 4. Login with invalid creds - EXPECT 401
r = test("Login invalid", "POST", "/auth/login", json={"email": "nope@nope.com", "password": "badpassword"})

# 5. Register - create test user
test_email = "local-test-user@example.com"
test_password = "TestPass123!"
test_name = "Local Test User"
r = test("Register test user", "POST", "/auth/register", json={"email": test_email, "password": test_password, "name": test_name})
if r and r.status_code == 200:
    token = r.json().get("access_token", "")
    print(f"    Got JWT (len={len(token)})")
elif r and r.status_code == 400:
    # email already registered — try login
    r2 = test("Login test user", "POST", "/auth/login", json={"email": test_email, "password": test_password})
    if r2 and r2.status_code == 200:
        token = r2.json().get("access_token", "")
        print(f"    Got JWT via login (len={len(token)})")
    else:
        token = ""
else:
    token = ""

headers = {"Authorization": f"Bearer {token}"} if token else {}

# 6. Profile with token
if token:
    r = test("Profile with token", "GET", "/auth/profile", headers=headers)

# 7. OAuth initiate (will redirect to error since not configured)
r = test("OAuth initiate (expect redirect/error)", "GET", "/auth/github", follow_redirects=False)
if r and r.status_code in (303, 307):
    print(f"    Location: {r.headers.get('Location')}")

# 8. Translation endpoint with token (will fail due to missing AI keys - check status code)
if token:
    r = test("Translation submit - AI failure expected", "POST", "/translations/", headers=headers, json={
        "source_code": "print('hello')",
        "source_language": "python",
        "target_language": "javascript"
    })

# 9. Review endpoint with token (will fail due to missing AI keys - check status code)
if token:
    r = test("Review submit - AI failure expected", "POST", "/reviews/", headers=headers, json={
        "code": "def foo(x): return x+1",
        "language": "python",
        "filename": "test.py"
    })

print("\n--- END OF SMOKE TEST ---")

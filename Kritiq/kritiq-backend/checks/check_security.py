from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("Security Controls Checker")
print("=" * 60)

# Register a test user
client.post(
    "/auth/register",
    json={
        "name": "Security User",
        "email": "security_test@example.com",
        "password": "Password@123"
    }
)

# Login to get a token
login_resp = client.post(
    "/auth/login",
    json={
        "email": "security_test@example.com",
        "password": "Password@123"
    }
)
token = login_resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"} if token else {}

# STEP 1: Invalid JWT
response = client.get("/reviews/74a2754d-6b19-4809-9069-b5bf8a48efcd", headers={"Authorization": "Bearer invalid_token"})
if response.status_code == 401:
    print("[SUCCESS] Invalid JWT rejected with 401")
else:
    print(f"[ERROR] Invalid JWT returned {response.status_code}")

# STEP 2: Missing JWT
response = client.get("/reviews/74a2754d-6b19-4809-9069-b5bf8a48efcd")
if response.status_code == 401:
    print("[SUCCESS] Missing JWT rejected with 401")
else:
    print(f"[ERROR] Missing JWT returned {response.status_code}")

# STEP 3: Malformed JSON
response = client.post("/auth/register", content="{invalid_json:")
if response.status_code in (400, 422):
    print("[SUCCESS] Malformed JSON rejected with 400/422")
else:
    print(f"[ERROR] Malformed JSON returned {response.status_code}")

# STEP 4: Large payload
large_payload = "A" * (1 * 1024 * 1024 + 100)  # > 1MB
response = client.post("/auth/register", content=large_payload)
if response.status_code == 413:
    print("[SUCCESS] Large payload rejected with 413")
else:
    print(f"[ERROR] Large payload returned {response.status_code}")

# STEP 5: Invalid ID/UUID format
response = client.get("/reviews/not-a-valid-uuid", headers=headers)
if response.status_code == 422:
    print("[SUCCESS] Malformed UUID rejected with 422")
else:
    print(f"[ERROR] Malformed UUID returned {response.status_code}")

# STEP 6: Rate Limiting
rate_limited = False
for _ in range(65):
    response = client.get("/reviews/74a2754d-6b19-4809-9069-b5bf8a48efcd", headers=headers)
    if response.status_code == 429:
        rate_limited = True
        break

if rate_limited:
    print("[SUCCESS] Rate limiting active: 429 triggered")
else:
    print("[ERROR] Rate limiting not triggered after 65 requests")

# STEP 7: Security Headers
response = client.get("/")
headers_resp = response.headers
required_headers = [
    ("X-Frame-Options", "DENY"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-XSS-Protection", "1; mode=block"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
]

headers_passed = True
for name, val in required_headers:
    if name not in headers_resp:
        print(f"[ERROR] Missing header: {name}")
        headers_passed = False
    elif headers_resp[name] != val:
        print(f"[ERROR] Header {name} has incorrect value: {headers_resp[name]} (expected {val})")
        headers_passed = False

if headers_passed:
    print("[SUCCESS] All advanced security headers present with correct values")

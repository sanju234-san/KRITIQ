import time
import os
import sys

print("=" * 60)
print("KRITIQ Final Release Verification Suite")
print("=" * 60)

passed = 0
failed = 0
warnings = 0

# 1. Startup & Import
start = time.perf_counter()
try:
    from app.main import app
    from app.core.config import settings
    elapsed = time.perf_counter() - start
    print(f"1. Application Startup & Config: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"1. Application Startup & Config: [FAIL] ({e})")
    failed += 1

# Initialize test client
from fastapi.testclient import TestClient
client = TestClient(app)

# 2. MongoDB connection
start = time.perf_counter()
try:
    from app.db.mongo_client import db_client
    db_client.get_collection("users")
    db_client.client.admin.command("ping")
    elapsed = time.perf_counter() - start
    print(f"2. MongoDB Connection: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"2. MongoDB Connection: [FAIL] ({e})")
    failed += 1

# 3. Database indexes
start = time.perf_counter()
try:
    users_idx = db_client.get_collection("users").index_information()
    assert "email_1" in users_idx
    elapsed = time.perf_counter() - start
    print(f"3. Database Indexes: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"3. Database Indexes: [FAIL] ({e})")
    failed += 1

# 4. Health endpoint
start = time.perf_counter()
try:
    response = client.get("/")
    assert response.status_code == 200
    assert "Kritiq API is running." in response.json()["message"]
    elapsed = time.perf_counter() - start
    print(f"4. Health Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"4. Health Endpoint: [FAIL] ({e})")
    failed += 1

# 5. User registration & login
start = time.perf_counter()
token = None
try:
    # Use unique email to avoid duplicates
    email = f"release_test_{int(time.time())}@example.com"
    reg_resp = client.post(
        "/auth/register",
        json={
            "name": "Release User",
            "email": email,
            "password": "Password@123"
        }
    )
    assert reg_resp.status_code == 200
    
    login_resp = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Password@123"
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None
    
    elapsed = time.perf_counter() - start
    print(f"5. Registration & Login Flow: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"5. Registration & Login Flow: [FAIL] ({e})")
    failed += 1

headers = {"Authorization": f"Bearer {token}"} if token else {}

# 6. JWT validation & protected endpoint
start = time.perf_counter()
try:
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email
    elapsed = time.perf_counter() - start
    print(f"6. JWT Validation & Profile Retrieve: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"6. JWT Validation & Profile Retrieve: [FAIL] ({e})")
    failed += 1

# 7. Swagger/OpenAPI checks
start = time.perf_counter()
try:
    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    openapi = openapi_resp.json()
    assert openapi.get("paths") is not None
    elapsed = time.perf_counter() - start
    print(f"7. OpenAPI Schema Validation: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"7. OpenAPI Schema Validation: [FAIL] ({e})")
    failed += 1

# 8. Rate limiter
start = time.perf_counter()
try:
    # Clear rate limiter cache
    from app.core.rate_limiter import global_limiter
    global_limiter.requests.clear()
    
    rate_limited = False
    for _ in range(65):
        resp = client.get("/auth/profile", headers=headers)
        if resp.status_code == 429:
            rate_limited = True
            break
    assert rate_limited is True
    elapsed = time.perf_counter() - start
    print(f"8. Rate Limiter Validation: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"8. Rate Limiter Validation: [FAIL] ({e})")
    failed += 1

# 9. Security headers
start = time.perf_counter()
try:
    response = client.get("/")
    h = response.headers
    assert h.get("X-Frame-Options") == "DENY"
    assert h.get("X-Content-Type-Options") == "nosniff"
    elapsed = time.perf_counter() - start
    print(f"9. Security Headers Validation: [PASS] ({elapsed:.4f}s)")
    passed += 1
except Exception as e:
    print(f"9. Security Headers Validation: [FAIL] ({e})")
    failed += 1

# Print final result summary
print("\n====================================")
print("RELEASE VERIFICATION SUMMARY")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Warnings: {warnings}")
print("====================================")

if failed > 0:
    print("[ERROR] RELEASE STATUS: REJECTED")
    sys.exit(1)
else:
    print("[SUCCESS] RELEASE STATUS: READY")
    sys.exit(0)

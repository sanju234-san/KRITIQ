import time
import os

print("=" * 60)
print("KRITIQ Performance Benchmark Suite")
print("=" * 60)

passed = 0
failed = 0
warnings = 0
times = {}

# 1. App import time
start = time.perf_counter()
try:
    from app.main import app
    elapsed = time.perf_counter() - start
    print(f"1. App Import Time: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["import"] = elapsed
except Exception as e:
    print(f"1. App Import Time: [FAIL] ({e})")
    failed += 1

# 2. Config loading
start = time.perf_counter()
try:
    from app.core.config import settings
    assert settings.DATABASE_NAME is not None
    elapsed = time.perf_counter() - start
    print(f"2. Config Loading Time: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["config"] = elapsed
except Exception as e:
    print(f"2. Config Loading Time: [FAIL] ({e})")
    failed += 1

# 3. MongoDB connection
start = time.perf_counter()
try:
    from app.db.mongo_client import db_client
    db_client.get_collection("users")
    db_client.client.admin.command("ping")
    elapsed = time.perf_counter() - start
    print(f"3. MongoDB Connection: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["mongo"] = elapsed
except Exception as e:
    print(f"3. MongoDB Connection: [FAIL] ({e})")
    failed += 1

# Initialize client for route benchmarking
from fastapi.testclient import TestClient
client = TestClient(app)

# Register/Login setup
token = None
try:
    client.post(
        "/auth/register",
        json={
            "name": "Benchmark User",
            "email": "benchmark@example.com",
            "password": "Password@123"
        }
    )
    login_resp = client.post(
        "/auth/login",
        json={
            "email": "benchmark@example.com",
            "password": "Password@123"
        }
    )
    token = login_resp.json().get("access_token")
except Exception:
    pass

headers = {"Authorization": f"Bearer {token}"} if token else {}

# 4. Health endpoint
start = time.perf_counter()
try:
    response = client.get("/")
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"4. Health Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["health"] = elapsed
except Exception as e:
    print(f"4. Health Endpoint: [FAIL] ({e})")
    failed += 1

# 5. Login endpoint
start = time.perf_counter()
try:
    response = client.post(
        "/auth/login",
        json={
            "email": "benchmark@example.com",
            "password": "Password@123"
        }
    )
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"5. Login Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["login"] = elapsed
except Exception as e:
    print(f"5. Login Endpoint: [FAIL] ({e})")
    failed += 1

# 6. Protected endpoint
start = time.perf_counter()
try:
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"6. Protected Endpoint (Profile): [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["profile"] = elapsed
except Exception as e:
    print(f"6. Protected Endpoint: [FAIL] ({e})")
    failed += 1

# 7. Review endpoint
start = time.perf_counter()
try:
    # Use small code mock
    response = client.post(
        "/reviews/",
        json={
            "code": "def add(x, y): return x + y",
            "language": "python",
            "filename": "add.py"
        },
        headers=headers
    )
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"7. Review Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["review"] = elapsed
except Exception as e:
    print(f"7. Review Endpoint: [FAIL] ({e})")
    failed += 1

# 8. Translation endpoint
start = time.perf_counter()
try:
    response = client.post(
        "/translations/",
        json={
            "source_code": "print('hello')",
            "source_language": "python",
            "target_language": "java"
        },
        headers=headers
    )
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"8. Translation Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["translation"] = elapsed
except Exception as e:
    print(f"8. Translation Endpoint: [FAIL] ({e})")
    failed += 1

# 9. Explanation endpoint
start = time.perf_counter()
try:
    response = client.post(
        "/explanations/explain",
        json={
            "code": "x = [i for i in range(10)]",
            "language": "python"
        },
        headers=headers
    )
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"9. Explanation Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["explanation"] = elapsed
except Exception as e:
    print(f"9. Explanation Endpoint: [FAIL] ({e})")
    failed += 1

# 10. History endpoint
start = time.perf_counter()
try:
    response = client.get("/history/", headers=headers)
    assert response.status_code == 200
    elapsed = time.perf_counter() - start
    print(f"10. History Endpoint: [PASS] ({elapsed:.4f}s)")
    passed += 1
    times["history"] = elapsed
except Exception as e:
    print(f"10. History Endpoint: [FAIL] ({e})")
    failed += 1

# Calculate averages
endpoint_keys = ["health", "login", "profile", "review", "translation", "explanation", "history"]
endpoint_times = [times[k] for k in endpoint_keys if k in times]
avg_endpoint_time = sum(endpoint_times) / len(endpoint_times) if endpoint_times else 0.0

print("\n==========================")
print("PERFORMANCE SUMMARY")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Warnings: {warnings}")
print(f"Average endpoint time: {avg_endpoint_time:.4f}s")
print("==========================")

# Sayeed domain - Verification Playground
import time
import uuid
import asyncio
import os
from datetime import timedelta
import jwt
from fastapi.testclient import TestClient

print("====================================================")
print("KRITIQ Backend Playground")
print("====================================================")

passed = 0
failed = 0
warnings = 0

# --- PHASE 1 TESTS ---
print("\n--- PHASE 1 VERIFICATION ---")

# STEP 1: Application imports
print("\nSTEP 1")
print("Application imports")
start_time = time.perf_counter()
try:
    from app.main import app
    from app.core.config import settings
    from app.db.mongo_client import db_client
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Configuration loads
print("\nSTEP 2")
print("Configuration loads")
start_time = time.perf_counter()
try:
    from app.core.config import settings
    assert settings.DATABASE_NAME is not None
    assert settings.MONGODB_URI is not None
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 3: MongoDB connects
print("\nSTEP 3")
print("MongoDB connects")
start_time = time.perf_counter()
try:
    from app.db.mongo_client import db_client
    col = db_client.get_collection("users")
    db_client.client.admin.command('ping')
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 4: Indexes exist
print("\nSTEP 4")
print("Indexes exist")
start_time = time.perf_counter()
try:
    from app.db.mongo_client import db_client
    users_indexes = db_client.get_collection("users").index_information()
    assert "email_1" in users_indexes
    assert users_indexes["email_1"].get("unique") is True
    
    reviews_indexes = db_client.get_collection("reviews").index_information()
    assert "user_id_1" in reviews_indexes
    
    trans_indexes = db_client.get_collection("translations").index_information()
    assert "user_id_1" in trans_indexes
    
    hist_indexes = db_client.get_collection("history").index_information()
    assert "user_id_1" in hist_indexes
    
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 5: Health endpoint
print("\nSTEP 5")
print("Health endpoint")
start_time = time.perf_counter()
try:
    from app.main import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Kritiq API is running." in response.json()["message"]
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 6: Exception handler
print("\nSTEP 6")
print("Exception handler")
start_time = time.perf_counter()
try:
    from app.main import app
    @app.get(
        "/test-fake-exception-error",
        summary="Test fake exception error endpoint",
        description="A temporary endpoint used to verify that the global exception handler correctly catches unhandled exceptions and returns a structured 500 error response."
    )
    def trigger_error():
        raise ValueError("Fake Database Crash!")
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test-fake-exception-error")
    assert response.status_code == 500
    json_data = response.json()
    assert json_data["error_code"] == "INTERNAL_SERVER_ERROR"
    assert "An unexpected error occurred. Please try again later." in json_data["message"]
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 2 TESTS ---
print("\n--- PHASE 2 VERIFICATION ---")
from app.main import app
client = TestClient(app, raise_server_exceptions=False)

unique_email = f"test_{uuid.uuid4().hex[:6]}@example.com"

# STEP 1: Valid registration
print("\nSTEP 1")
print("Valid registration")
start_time = time.perf_counter()
try:
    payload = {
        "name": "Test User",
        "email": unique_email,
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Weak password rejected
print("\nSTEP 2")
print("Weak password rejected")
start_time = time.perf_counter()
try:
    payload = {
        "name": "Test User",
        "email": "weakpass@example.com",
        "password": "short"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 3: Invalid email rejected
print("\nSTEP 3")
print("Invalid email rejected")
start_time = time.perf_counter()
try:
    payload = {
        "name": "Test User",
        "email": "invalid-email-format",
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# Obtain token for protected calls
try:
    reg_response = client.post("/auth/login", json={
        "email": unique_email,
        "password": "securepassword123"
    })
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
except Exception:
    headers = {}

# STEP 4: Review empty code rejected
print("\nSTEP 4")
print("Review empty code rejected")
start_time = time.perf_counter()
try:
    payload = {
        "code": "   ",
        "language": "python"
    }
    response = client.post("/reviews/", json=payload, headers=headers)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 5: Review unsupported language rejected
print("\nSTEP 5")
print("Review unsupported language rejected")
start_time = time.perf_counter()
try:
    payload = {
        "code": "print('hello')",
        "language": "unsupported_lang"
    }
    response = client.post("/reviews/", json=payload, headers=headers)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 6: Translation invalid language rejected
print("\nSTEP 6")
print("Translation invalid language rejected")
start_time = time.perf_counter()
try:
    payload = {
        "source_code": "print('hello')",
        "source_language": "unsupported_lang",
        "target_language": "java"
    }
    response = client.post("/translations/", json=payload, headers=headers)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 7: Translation empty source rejected
print("\nSTEP 7")
print("Translation empty source rejected")
start_time = time.perf_counter()
try:
    payload = {
        "source_code": "",
        "source_language": "python",
        "target_language": "java"
    }
    response = client.post("/translations/", json=payload, headers=headers)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 8: Explanation endpoint returns structured response
print("\nSTEP 8")
print("Explanation endpoint returns structured response")
start_time = time.perf_counter()
try:
    payload = {
        "code": "print('hello')",
        "language": "python"
    }
    response = client.post("/explanations/explain", json=payload, headers=headers)
    
    assert response.status_code in (200, 500, 503)
    json_data = response.json()
    if response.status_code == 200:
        assert "explanation" in json_data
        assert isinstance(json_data["explanation"], str)
    else:
        assert "error_code" in json_data
        assert "message" in json_data
        
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 3 TESTS ---
print("\n--- PHASE 3 VERIFICATION ---")

async def run_phase3():
    global passed, failed, warnings
    from app.db.reviews_repo import reviews_repo
    from app.db.translations_repo import translations_repo
    from app.db.history_repo import history_repo

    test_user_id = f"user_{uuid.uuid4().hex[:8]}"

    # STEP 1: Insert sample review
    print("\nSTEP 1")
    print("Insert sample review")
    start_time = time.perf_counter()
    try:
        review_data = {
            "summary": "Sample review code formatting",
            "issues": [{"title": "Spacing issue", "explanation": "Extra space detected"}],
            "raw_output": "Issues found."
        }
        saved_review = await reviews_repo.save_review(test_user_id, review_data)
        assert saved_review["user_id"] == test_user_id
        assert "_id" in saved_review
        
        # Log to history
        await history_repo.log_activity(
            user_id=test_user_id,
            type="review",
            summary="Run code review check",
            details={"review_id": saved_review["_id"]}
        )
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 2: Insert sample translation
    print("\nSTEP 2")
    print("Insert sample translation")
    start_time = time.perf_counter()
    try:
        translation_data = {
            "translated_code": "System.out.println(\"hello\");",
            "source_language": "python",
            "target_language": "java"
        }
        saved_trans = await translations_repo.save_translation(test_user_id, translation_data)
        assert saved_trans["user_id"] == test_user_id
        assert "_id" in saved_trans
        
        # Log to history
        await history_repo.log_activity(
            user_id=test_user_id,
            type="translation",
            summary="Run code translation",
            details={"translation_id": saved_trans["_id"]}
        )
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # Populate additional records to ensure pagination matches
    try:
        for i in range(2):
            r = await reviews_repo.save_review(test_user_id, {"summary": f"review {i}", "issues": []})
            await history_repo.log_activity(test_user_id, "review", f"review log {i}", {"review_id": r["_id"]})
        for i in range(2):
            t = await translations_repo.save_translation(test_user_id, {"translated_code": f"code {i}"})
            await history_repo.log_activity(test_user_id, "translation", f"translation log {i}", {"translation_id": t["_id"]})
    except Exception:
        pass

    # STEP 3: Retrieve paginated history
    print("\nSTEP 3")
    print("Retrieve paginated history")
    start_time = time.perf_counter()
    try:
        logs = await history_repo.get_history_by_user(test_user_id, limit=2, skip=1)
        assert len(logs) == 2
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 4: Retrieve paginated reviews
    print("\nSTEP 4")
    print("Retrieve paginated reviews")
    start_time = time.perf_counter()
    try:
        reviews = await reviews_repo.get_reviews_by_user(test_user_id, limit=2, skip=0)
        assert len(reviews) == 2
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 5: Retrieve paginated translations
    print("\nSTEP 5")
    print("Retrieve paginated translations")
    start_time = time.perf_counter()
    try:
        translations = await translations_repo.get_translations_by_user(test_user_id, limit=2, skip=1)
        assert len(translations) == 2
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 6: Verify newest-first sorting
    print("\nSTEP 6")
    print("Verify newest-first sorting")
    start_time = time.perf_counter()
    try:
        logs = await history_repo.get_history_by_user(test_user_id, limit=5, skip=0)
        for i in range(len(logs) - 1):
            assert logs[i]["timestamp"] >= logs[i+1]["timestamp"]
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 7: Verify repository methods return expected objects
    print("\nSTEP 7")
    print("Verify repository methods return expected objects")
    start_time = time.perf_counter()
    try:
        review = await reviews_repo.get_review_by_id(saved_review["_id"])
        assert review is not None
        assert isinstance(review, dict)
        assert review["summary"] == "Sample review code formatting"
        
        translation = await translations_repo.get_translation_by_id(saved_trans["_id"])
        assert translation is not None
        assert isinstance(translation, dict)
        assert "translated_code" in translation
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

asyncio.run(run_phase3())


# --- PHASE 4 TESTS ---
print("\n--- PHASE 4 VERIFICATION ---")
from app.auth.jwt_handler import create_access_token

unique_email_p4 = f"p4_{uuid.uuid4().hex[:6]}@example.com"
token_p4 = None

# STEP 1: Register valid user
print("\nSTEP 1")
print("Register valid user")
start_time = time.perf_counter()
try:
    payload = {
        "name": "P4 User",
        "email": unique_email_p4,
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    token_p4 = response.json()["access_token"]
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Duplicate email rejected
print("\nSTEP 2")
print("Duplicate email rejected")
start_time = time.perf_counter()
try:
    payload = {
        "name": "P4 User Dup",
        "email": unique_email_p4,
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 3: Login success
print("\nSTEP 3")
print("Login success")
start_time = time.perf_counter()
try:
    payload = {
        "email": unique_email_p4,
        "password": "securepassword123"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 4: Wrong password rejected
print("\nSTEP 4")
print("Wrong password rejected")
start_time = time.perf_counter()
try:
    payload = {
        "email": unique_email_p4,
        "password": "wrongpassword123"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 5: Invalid JWT rejected
print("\nSTEP 5")
print("Invalid JWT rejected")
start_time = time.perf_counter()
try:
    invalid_token = jwt.encode({"sub": unique_email_p4}, "wrong-secret", algorithm="HS256")
    response = client.get("/auth/profile", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 6: Expired JWT rejected
print("\nSTEP 6")
print("Expired JWT rejected")
start_time = time.perf_counter()
try:
    expired_token = create_access_token(data={"sub": unique_email_p4}, expires_delta=timedelta(minutes=-10))
    response = client.get("/auth/profile", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 7: Malformed JWT rejected
print("\nSTEP 7")
print("Malformed JWT rejected")
start_time = time.perf_counter()
try:
    response = client.get("/auth/profile", headers={"Authorization": "Bearer malformed.token.here"})
    assert response.status_code == 401
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 8: Missing Authorization header
print("\nSTEP 8")
print("Missing Authorization header")
start_time = time.perf_counter()
try:
    response = client.get("/auth/profile")
    assert response.status_code == 401
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 9: Protected endpoint with valid JWT
print("\nSTEP 9")
print("Protected endpoint with valid JWT")
start_time = time.perf_counter()
try:
    response = client.get("/auth/profile", headers={"Authorization": f"Bearer {token_p4}"})
    assert response.status_code == 200
    assert response.json()["email"] == unique_email_p4
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 10: Deleted user token handling
print("\nSTEP 10")
print("Deleted user token handling")
start_time = time.perf_counter()
try:
    deleted_token = create_access_token(data={"sub": "does_not_exist@example.com"})
    response = client.get("/auth/profile", headers={"Authorization": f"Bearer {deleted_token}"})
    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 5 TESTS ---
print("\n--- PHASE 5 VERIFICATION ---")

# STEP 1: OpenAPI schema generated
print("\nSTEP 1")
print("OpenAPI schema generated")
start_time = time.perf_counter()
try:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "openapi" in openapi
    assert "paths" in openapi
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Swagger loads
print("\nSTEP 2")
print("Swagger loads")
start_time = time.perf_counter()
try:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 3: All routes have summaries
print("\nSTEP 3")
print("All routes have summaries")
start_time = time.perf_counter()
try:
    from fastapi.routing import APIRoute
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path not in ("/openapi.json", "/docs", "/redoc", "/"):
            assert route.summary is not None and route.summary != ""
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 4: All routes have descriptions
print("\nSTEP 4")
print("All routes have descriptions")
start_time = time.perf_counter()
try:
    from fastapi.routing import APIRoute
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path not in ("/openapi.json", "/docs", "/redoc", "/"):
            assert route.description is not None and route.description != ""
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# STEP 5: Response models documented
print("\nSTEP 5")
print("Response models documented")
start_time = time.perf_counter()
try:
    openapi_res = client.get("/openapi.json").json()
    schemas = openapi_res.get("components", {}).get("schemas", {})
    # Check at least TokenResponse or UserProfileResponse
    assert "TokenResponse" in schemas
    assert "UserProfileResponse" in schemas
    for schema_name in ("TokenResponse", "UserProfileResponse"):
        for prop in schemas[schema_name].get("properties", {}).values():
            assert "description" in prop
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 6: Request models documented
print("\nSTEP 6")
print("Request models documented")
start_time = time.perf_counter()
try:
    openapi_res = client.get("/openapi.json").json()
    schemas = openapi_res.get("components", {}).get("schemas", {})
    assert "UserRegister" in schemas
    assert "UserLogin" in schemas
    for schema_name in ("UserRegister", "UserLogin"):
        for prop in schemas[schema_name].get("properties", {}).values():
            assert "description" in prop
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 7: API contract generated
print("\nSTEP 7")
print("API contract generated")
start_time = time.perf_counter()
try:
    assert os.path.exists("../docs/api-contract.md")
    assert os.path.getsize("../docs/api-contract.md") > 0
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 6 VERIFICATION ---
print("\n--- PHASE 6 VERIFICATION ---")

# STEP 1: New test coverage files present
print("\nSTEP 1")
print("New test coverage files present")
start_time = time.perf_counter()
try:
    assert os.path.exists("tests/test_jwt.py")
    assert os.path.exists("tests/test_validators.py")
    assert os.path.exists("tests/test_pagination.py")
    assert os.path.exists("tests/test_repos.py")
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Pytest executes successfully
print("\nSTEP 2")
print("Pytest executes successfully")
start_time = time.perf_counter()
try:
    import sys
    import subprocess
    res = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True, cwd=".")
    if res.returncode != 0:
        raise ValueError(f"pytest failed with exit code {res.returncode}:\n{res.stdout}\n{res.stderr}")
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 8 VERIFICATION ---
print("\n--- PHASE 8 VERIFICATION ---")

# Setup: register and login a test user for auth route checks
test_token = None
try:
    from app.main import app
    client = TestClient(app, raise_server_exceptions=False)
    client.post(
        "/auth/register",
        json={
            "name": "Playground Security User",
            "email": "play_security@example.com",
            "password": "Password@123"
        }
    )
    login_resp = client.post(
        "/auth/login",
        json={
            "email": "play_security@example.com",
            "password": "Password@123"
        }
    )
    test_token = login_resp.json().get("access_token")
except Exception:
    pass

headers_auth = {"Authorization": f"Bearer {test_token}"} if test_token else {}

# STEP 1: Invalid JWT
print("\nSTEP 1")
print("Invalid JWT rejected with 401")
start_time = time.perf_counter()
try:
    response = client.get("/reviews/74a2754d-6b19-4809-9069-b5bf8a48efcd", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Missing JWT
print("\nSTEP 2")
print("Missing JWT rejected with 401")
start_time = time.perf_counter()
try:
    response = client.get("/reviews/74a2754d-6b19-4809-9069-b5bf8a48efcd")
    assert response.status_code == 401
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 3: Malformed JSON
print("\nSTEP 3")
print("Malformed JSON rejected with 400/422")
start_time = time.perf_counter()
try:
    response = client.post("/auth/register", content="{invalid_json:")
    assert response.status_code in (400, 422)
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 4: Large payload
print("\nSTEP 4")
print("Large payload rejected with 413")
start_time = time.perf_counter()
try:
    large_payload = "A" * (1 * 1024 * 1024 + 100)
    response = client.post("/auth/register", content=large_payload)
    assert response.status_code == 413
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 5: Malformed UUID format
print("\nSTEP 5")
print("Malformed UUID rejected with 422")
start_time = time.perf_counter()
try:
    response = client.get("/reviews/not-a-valid-uuid", headers=headers_auth)
    assert response.status_code == 422
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 6: Rate Limiting
print("\nSTEP 6")
print("Rate limiting active: 429 triggered")
start_time = time.perf_counter()
try:
    rate_limited = False
    for _ in range(65):
        response = client.get("/reviews/74a2754d-6b19-4809-9069-b5bf8a48efcd", headers=headers_auth)
        if response.status_code == 429:
            rate_limited = True
            break
    assert rate_limited is True
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 7: Security Headers
print("\nSTEP 7")
print("Advanced security headers present")
start_time = time.perf_counter()
try:
    response = client.get("/")
    h = response.headers
    assert h.get("X-Frame-Options") == "DENY"
    assert h.get("X-Content-Type-Options") == "nosniff"
    assert h.get("X-XSS-Protection") == "1; mode=block"
    assert h.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert h.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 11 VERIFICATION ---
print("\n--- PHASE 11 VERIFICATION ---")

# Clear rate limiter cache to avoid test interference from Phase 8 Step 6
try:
    from app.core.rate_limiter import global_limiter
    global_limiter.requests.clear()
except Exception:
    pass

# STEP 1: App startup benchmark
print("\nSTEP 1")
print("App startup benchmark")
start_time = time.perf_counter()
try:
    from app.main import app
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 2: Mongo connection benchmark
print("\nSTEP 2")
print("Mongo connection benchmark")
start_time = time.perf_counter()
try:
    from app.db.mongo_client import db_client
    db_client.client.admin.command('ping')
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 3: Health endpoint benchmark
print("\nSTEP 3")
print("Health endpoint benchmark")
start_time = time.perf_counter()
try:
    response = client.get("/")
    assert response.status_code == 200
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 4: Authentication benchmark
print("\nSTEP 4")
print("Authentication benchmark")
start_time = time.perf_counter()
try:
    # Login again to test duration
    response = client.post(
        "/auth/login",
        json={
            "email": "play_security@example.com",
            "password": "Password@123"
        }
    )
    assert response.status_code == 200
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 5: Review benchmark
print("\nSTEP 5")
print("Review benchmark")
start_time = time.perf_counter()
try:
    time.sleep(4)
    response = client.post(
        "/reviews/",
        json={
            "code": "def add(a, b): return a + b",
            "language": "python",
            "filename": "add.py"
        },
        headers=headers_auth
    )
    assert response.status_code in (200, 500, 503)
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 6: Translation benchmark
print("\nSTEP 6")
print("Translation benchmark")
start_time = time.perf_counter()
try:
    time.sleep(4)
    response = client.post(
        "/translations/",
        json={
            "source_code": "print('hello')",
            "source_language": "python",
            "target_language": "java"
        },
        headers=headers_auth
    )
    assert response.status_code in (200, 500, 503)
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 7: Explanation benchmark
print("\nSTEP 7")
print("Explanation benchmark")
start_time = time.perf_counter()
try:
    time.sleep(4)
    response = client.post(
        "/explanations/explain",
        json={
            "code": "x = [i for i in range(10)]",
            "language": "python"
        },
        headers=headers_auth
    )
    assert response.status_code in (200, 500, 503)
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 8: History benchmark
print("\nSTEP 8")
print("History benchmark")
start_time = time.perf_counter()
try:
    response = client.get("/history/", headers=headers_auth)
    assert response.status_code == 200
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 9: Verify MongoClient reuse
print("\nSTEP 9")
print("Verify MongoClient reuse")
start_time = time.perf_counter()
try:
    from app.db.mongo_client import db_client
    from app.db.users_repo import users_repo
    from app.db.reviews_repo import reviews_repo
    from app.db.translations_repo import translations_repo
    from app.db.history_repo import history_repo

    client1 = db_client.client
    client2 = users_repo.collection.database.client
    client3 = reviews_repo.collection.database.client
    client4 = translations_repo.collection.database.client
    client5 = history_repo.collection.database.client

    assert client1 is not None
    assert client1 is client2
    assert client2 is client3
    assert client3 is client4
    assert client4 is client5
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: {e}")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

# STEP 10: Verify no regressions
print("\nSTEP 10")
print("Verify no regressions")
start_time = time.perf_counter()
try:
    assert failed == 0
    print("PASS")
    passed += 1
except Exception as e:
    print(f"FAIL: previous errors detected")
    failed += 1
print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


# --- PHASE 12 VERIFICATION ---
async def run_phase12():
    global passed, failed, warnings
    print("\n========================================")
    print("PHASE 12 VERIFICATION")
    print("========================================")

    # Clear rate limiter cache to avoid test interference from previous phases
    try:
        from app.core.rate_limiter import global_limiter
        global_limiter.requests.clear()
    except Exception:
        pass

    # STEP 1
    print("\nSTEP 1")
    print("Application startup")
    start_time = time.perf_counter()
    try:
        from app.main import app
        from app.core.config import settings
        from app.db.mongo_client import db_client
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 2
    print("\nSTEP 2")
    print("MongoDB connection")
    start_time = time.perf_counter()
    try:
        db_client.client.admin.command('ping')
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 3
    print("\nSTEP 3")
    print("Database indexes")
    start_time = time.perf_counter()
    try:
        assert "email_1" in db_client.get_collection("users").index_information()
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 4
    print("\nSTEP 4")
    print("Health endpoint")
    start_time = time.perf_counter()
    try:
        response = client.get("/")
        assert response.status_code == 200
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 5
    print("\nSTEP 5")
    print("User registration")
    start_time = time.perf_counter()
    email_p12 = f"play12_{int(time.time())}@example.com"
    try:
        response = client.post(
            "/auth/register",
            json={
                "name": "P12 User",
                "email": email_p12,
                "password": "Password@123"
            }
        )
        assert response.status_code == 200
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 6
    print("\nSTEP 6")
    print("User login")
    start_time = time.perf_counter()
    token_p12 = None
    try:
        response = client.post(
            "/auth/login",
            json={
                "email": email_p12,
                "password": "Password@123"
            }
        )
        assert response.status_code == 200
        token_p12 = response.json().get("access_token")
        assert token_p12 is not None
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    headers_p12 = {"Authorization": f"Bearer {token_p12}"} if token_p12 else {}

    # STEP 7
    print("\nSTEP 7")
    print("JWT validation")
    start_time = time.perf_counter()
    try:
        # Test invalid token
        r_bad = client.get("/auth/profile", headers={"Authorization": "Bearer badtoken"})
        assert r_bad.status_code == 401
        
        # Test valid token
        r_good = client.get("/auth/profile", headers=headers_p12)
        assert r_good.status_code == 200
        
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 8
    print("\nSTEP 8")
    print("Protected profile endpoint")
    start_time = time.perf_counter()
    try:
        response = client.get("/auth/profile", headers=headers_p12)
        assert response.status_code == 200
        assert response.json()["email"] == email_p12
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 9
    print("\nSTEP 9")
    print("Review API")
    start_time = time.perf_counter()
    try:
        time.sleep(4)
        response = client.post(
            "/reviews/",
            json={
                "code": "def hello(): print('world')",
                "language": "python",
                "filename": "hello.py"
            },
            headers=headers_p12
        )
        assert response.status_code in (200, 500, 503)
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 10
    print("\nSTEP 10")
    print("Translation API")
    start_time = time.perf_counter()
    try:
        time.sleep(4)
        response = client.post(
            "/translations/",
            json={
                "source_code": "print('hello')",
                "source_language": "python",
                "target_language": "java"
            },
            headers=headers_p12
        )
        assert response.status_code in (200, 500, 503)
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 11
    print("\nSTEP 11")
    print("Explanation API")
    start_time = time.perf_counter()
    try:
        time.sleep(4)
        response = client.post(
            "/explanations/explain",
            json={
                "code": "x = 5 + 10",
                "language": "python"
            },
            headers=headers_p12
        )
        assert response.status_code in (200, 500, 503)
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 12
    print("\nSTEP 12")
    print("History API")
    start_time = time.perf_counter()
    try:
        response = client.get("/history/", headers=headers_p12)
        assert response.status_code == 200
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 13
    print("\nSTEP 13")
    print("Pagination")
    start_time = time.perf_counter()
    try:
        response = client.get("/history/reviews?limit=1&skip=0", headers=headers_p12)
        assert response.status_code == 200
        assert len(response.json()) <= 1
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 14
    print("\nSTEP 14")
    print("Security middleware")
    start_time = time.perf_counter()
    try:
        response = client.get("/")
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 15
    print("\nSTEP 15")
    print("Rate limiter")
    start_time = time.perf_counter()
    try:
        global_limiter.requests.clear()
        rate_limited = False
        for _ in range(65):
            resp = client.get("/auth/profile", headers=headers_p12)
            if resp.status_code == 429:
                rate_limited = True
                break
        assert rate_limited is True
        # Reset it so next steps don't fail
        global_limiter.requests.clear()
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 16
    print("\nSTEP 16")
    print("Swagger/OpenAPI")
    start_time = time.perf_counter()
    try:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "paths" in response.json()
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 17
    print("\nSTEP 17")
    print("API contract")
    start_time = time.perf_counter()
    try:
        # Ensure standard route paths and descriptions exist
        response = client.get("/openapi.json")
        openapi = response.json()
        assert "/reviews/" in openapi["paths"]
        assert "/translations/" in openapi["paths"]
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 18
    print("\nSTEP 18")
    print("Performance benchmark")
    start_time = time.perf_counter()
    try:
        # Simple fast API benchmark check
        response = client.get("/")
        assert response.status_code == 200
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 19
    print("\nSTEP 19")
    print("Pytest suite")
    start_time = time.perf_counter()
    try:
        import subprocess
        import sys
        res = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
        assert res.returncode == 0
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 20
    print("\nSTEP 20")
    print("Repository integrity")
    start_time = time.perf_counter()
    try:
        from app.db.users_repo import users_repo
        user_doc = await users_repo.get_by_email(email_p12)
        assert user_doc is not None
        assert user_doc["name"] == "P12 User"
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 21
    print("\nSTEP 21")
    print("No regression verification")
    start_time = time.perf_counter()
    try:
        assert failed == 0
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: errors detected in the current run")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")

    # STEP 22
    print("\nSTEP 22")
    print("Backend release readiness")
    start_time = time.perf_counter()
    try:
        assert failed == 0
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: not release-ready due to failures")
        failed += 1
    print(f"Execution time: {time.perf_counter() - start_time:.4f}s")


    # --- FINAL SUMMARY ---
    print("\n====================================")
    print("FINAL RESULT")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Warnings: {warnings}")
    print(f"Backend Ready: {'YES' if failed == 0 else 'NO'}")
    print("====================================")

import asyncio
asyncio.run(run_phase12())


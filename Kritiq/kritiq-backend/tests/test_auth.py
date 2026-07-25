# SHARED - Sayeed domain - Auth tests
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.users_repo import users_repo

client = TestClient(app)

MOCK_USERS_DB = {}

@pytest.fixture(autouse=True)
def mock_db_methods(monkeypatch):
    async def mock_get_by_email(email: str):
        return MOCK_USERS_DB.get(email)

    async def mock_create_user(user_data: dict):
        user_copy = user_data.copy()
        user_copy["_id"] = "mock_user_id_123"
        MOCK_USERS_DB[user_data["email"]] = user_copy
        return user_copy

    monkeypatch.setattr(users_repo, "get_by_email", mock_get_by_email)
    monkeypatch.setattr(users_repo, "create_user", mock_create_user)
    MOCK_USERS_DB.clear()

def test_user_registration_and_login():
    register_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

    response_duplicate = client.post("/auth/register", json=register_payload)
    assert response_duplicate.status_code == 400
    assert response_duplicate.json()["detail"] == "Email already registered"

    login_payload = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    response_login = client.post("/auth/login", json=login_payload)
    assert response_login.status_code == 200
    login_token = response_login.json()["access_token"]

    response_bad_login = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response_bad_login.status_code == 401
    assert response_bad_login.json()["detail"] == "Invalid email or password"

    headers = {"Authorization": f"Bearer {login_token}"}
    response_profile = client.get("/auth/profile", headers=headers)
    assert response_profile.status_code == 200
    profile_data = response_profile.json()
    assert profile_data["email"] == "test@example.com"
    assert profile_data["name"] == "Test User"
    assert profile_data["id"] == "mock_user_id_123"


import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo

client = TestClient(app)

MOCK_HISTORY = [
    {"_id": "log1", "user_id": "user999", "type": "review", "timestamp": "2026-07-08T18:00:00Z", "summary": "Review", "details": {}},
    {"_id": "log2", "user_id": "user999", "type": "translation", "timestamp": "2026-07-08T17:00:00Z", "summary": "Translate", "details": {}},
    {"_id": "log3", "user_id": "user999", "type": "explanation", "timestamp": "2026-07-08T16:00:00Z", "summary": "Explain", "details": {}},
]

@pytest.fixture(autouse=True)
def mock_auth_and_history_repo(monkeypatch):
    async def mock_get_current_user():
        return {"_id": "user999", "name": "Tester", "email": "tester@example.com"}
    
    async def mock_get_history_by_user(user_id: str, limit: int = 20, skip: int = 0, activity_type: str = None):
        filtered = [item for item in MOCK_HISTORY if item["user_id"] == user_id]
        if activity_type:
            filtered = [item for item in filtered if item["type"] == activity_type]
        return filtered[skip:skip + limit]

    app.dependency_overrides[get_current_user] = mock_get_current_user
    monkeypatch.setattr(history_repo, "get_history_by_user", mock_get_history_by_user)
    yield
    app.dependency_overrides.clear()

def test_history_pagination_success():
    # Fetch first 2
    response = client.get("/history/?limit=2&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 2
    assert data["history"][0]["id"] == "log1"
    assert data["history"][1]["id"] == "log2"

    # Skip 1, fetch 2
    response_skip = client.get("/history/?limit=2&skip=1")
    assert response_skip.status_code == 200
    data_skip = response_skip.json()
    assert len(data_skip["history"]) == 2
    assert data_skip["history"][0]["id"] == "log2"
    assert data_skip["history"][1]["id"] == "log3"

def test_history_filter_by_type():
    response = client.get("/history/?type=review")
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 1
    assert data["history"][0]["type"] == "review"

def test_history_out_of_bounds_validation():
    # Negative limit
    response = client.get("/history/?limit=-5")
    assert response.status_code == 422

    # Limit too large
    response_large = client.get("/history/?limit=200")
    assert response_large.status_code == 422

    # Negative skip
    response_skip_neg = client.get("/history/?skip=-1")
    assert response_skip_neg.status_code == 422

# SHARED - Sayeed domain - Review & Other endpoint integration tests
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.dependencies import get_current_user
from app.db.reviews_repo import reviews_repo
from app.db.translations_repo import translations_repo
from app.db.history_repo import history_repo
from ai_agent import review_service, translation_service, explanation_service

client = TestClient(app)

MOCK_REVIEWS_DB = {}
MOCK_TRANSLATIONS_DB = {}
MOCK_HISTORY_DB = []

@pytest.fixture(autouse=True)
def override_auth_dependency():
    async def mock_get_current_user():
        return {
            "_id": "test_user_id_999",
            "name": "Developer",
            "email": "dev@example.com"
        }
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_db_and_services(monkeypatch):
    async def mock_save_review(user_id: str, review_data: dict):
        review_data["_id"] = "mock_review_uuid"
        review_data["user_id"] = user_id
        MOCK_REVIEWS_DB["mock_review_uuid"] = review_data
        return review_data

    async def mock_get_review_by_id(review_id: str):
        return MOCK_REVIEWS_DB.get(review_id)

    async def mock_save_translation(user_id: str, translation_data: dict):
        translation_data["_id"] = "mock_translation_uuid"
        translation_data["user_id"] = user_id
        MOCK_TRANSLATIONS_DB["mock_translation_uuid"] = translation_data
        return translation_data

    async def mock_get_translation_by_id(translation_id: str):
        return MOCK_TRANSLATIONS_DB.get(translation_id)

    async def mock_log_activity(user_id: str, type: str, summary: str, details: dict):
        log_data = {
            "_id": "mock_log_uuid",
            "user_id": user_id,
            "type": type,
            "summary": summary,
            "details": details,
            "timestamp": "2026-07-08T18:00:00Z"
        }
        MOCK_HISTORY_DB.append(log_data)
        return log_data

    async def mock_get_history_by_user(user_id: str, *args, **kwargs):
        return [log for log in MOCK_HISTORY_DB if log["user_id"] == user_id]

    async def mock_get_reviews_by_user(user_id: str, *args, **kwargs):
        return [rev for rev in MOCK_REVIEWS_DB.values() if rev["user_id"] == user_id]

    async def mock_get_translations_by_user(user_id: str, *args, **kwargs):
        return [trans for trans in MOCK_TRANSLATIONS_DB.values() if trans["user_id"] == user_id]

    monkeypatch.setattr(reviews_repo, "save_review", mock_save_review)
    monkeypatch.setattr(reviews_repo, "get_review_by_id", mock_get_review_by_id)
    monkeypatch.setattr(reviews_repo, "get_reviews_by_user", mock_get_reviews_by_user)
    monkeypatch.setattr(translations_repo, "save_translation", mock_save_translation)
    monkeypatch.setattr(translations_repo, "get_translation_by_id", mock_get_translation_by_id)
    monkeypatch.setattr(translations_repo, "get_translations_by_user", mock_get_translations_by_user)
    monkeypatch.setattr(history_repo, "log_activity", mock_log_activity)
    monkeypatch.setattr(history_repo, "get_history_by_user", mock_get_history_by_user)

    def mock_review_code(code: str, language: str = "python") -> str:
        return "Summary: Mocked review.\nIssues:\n1. Unused Variable - Line 12 has an unused variable. Remove it."

    def mock_translate_code(code: str, source_lang: str, target_lang: str) -> str:
        return "public class Mock {}"

    def mock_explain_code(code: str, language: str = "python") -> str:
        return "This is a mocked explanation."

    monkeypatch.setattr("app.routes.review_routes.review_code", mock_review_code)
    monkeypatch.setattr("app.routes.translation_routes.translate_code", mock_translate_code)
    monkeypatch.setattr("app.routes.explanation_routes.explain_code", mock_explain_code)

    MOCK_REVIEWS_DB.clear()
    MOCK_TRANSLATIONS_DB.clear()
    MOCK_HISTORY_DB.clear()

def test_code_review_routes():
    payload = {
        "code": "def test(): pass",
        "language": "python",
        "filename": "test.py"
    }
    response = client.post("/reviews/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["review_id"] == "mock_review_uuid"
    assert data["summary"] == "Mocked review."
    assert len(data["issues"]) == 1
    assert data["issues"][0]["title"] == "Unused Variable"
    assert data["issues"][0]["line"] == 12

    get_response = client.get("/reviews/mock_review_uuid")
    assert get_response.status_code == 200
    assert get_response.json()["review_id"] == "mock_review_uuid"

    get_response_404 = client.get("/reviews/nonexistent_id")
    assert get_response_404.status_code == 404

def test_code_translation_routes():
    payload = {
        "source_code": "def add(a, b): return a + b",
        "source_language": "python",
        "target_language": "java"
    }
    response = client.post("/translations/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["translation_id"] == "mock_translation_uuid"
    assert data["translated_code"] == "public class Mock {}"

    get_response = client.get("/translations/mock_translation_uuid")
    assert get_response.status_code == 200
    assert get_response.json()["translation_id"] == "mock_translation_uuid"

def test_code_explanation_routes():
    payload = {
        "code": "print('hello')",
        "language": "python"
    }
    response = client.post("/explanations/explain", json=payload)
    assert response.status_code == 200
    assert response.json()["explanation"] == "This is a mocked explanation."

def test_history_routes():
    client.post("/reviews/", json={"code": "x = 1"})
    client.post("/translations/", json={
        "source_code": "print('hello')",
        "source_language": "python",
        "target_language": "java"
    })
    
    # 1. Combined history timeline
    response = client.get("/history/")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert len(data["history"]) == 2

    # 2. Reviews only history
    response_reviews = client.get("/history/reviews")
    assert response_reviews.status_code == 200
    reviews_data = response_reviews.json()
    assert len(reviews_data) == 1
    assert reviews_data[0]["review_id"] == "mock_review_uuid"

    # 3. Translations only history
    response_trans = client.get("/history/translations")
    assert response_trans.status_code == 200
    trans_data = response_trans.json()
    assert len(trans_data) == 1
    assert trans_data[0]["translation_id"] == "mock_translation_uuid"



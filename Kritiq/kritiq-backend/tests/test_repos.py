import pytest
from unittest.mock import MagicMock
from app.db.users_repo import users_repo
from app.db.reviews_repo import reviews_repo
from app.db.translations_repo import translations_repo
from app.db.history_repo import history_repo

@pytest.fixture
def mock_db_collections(monkeypatch):
    mock_users = MagicMock()
    mock_reviews = MagicMock()
    mock_translations = MagicMock()
    mock_history = MagicMock()

    # Monkeypatch the collection properties in the repos
    monkeypatch.setattr(users_repo, "_collection", mock_users)
    monkeypatch.setattr(reviews_repo, "_collection", mock_reviews)
    monkeypatch.setattr(translations_repo, "_collection", mock_translations)
    monkeypatch.setattr(history_repo, "_collection", mock_history)

    return {
        "users": mock_users,
        "reviews": mock_reviews,
        "translations": mock_translations,
        "history": mock_history
    }

@pytest.mark.asyncio
async def test_users_repo(mock_db_collections):
    col = mock_db_collections["users"]
    
    # 1. get_by_email
    col.find_one.return_value = {"email": "test@example.com", "name": "Test"}
    res = await users_repo.get_by_email("test@example.com")
    assert res["name"] == "Test"
    col.find_one.assert_called_with({"email": "test@example.com"})

    # 2. create_user
    def mock_insert(doc):
        doc["_id"] = "user_id_1"
        return MagicMock(inserted_id="user_id_1")
    col.insert_one.side_effect = mock_insert
    user_data = {"email": "new@example.com", "name": "New"}
    res_create = await users_repo.create_user(user_data)
    assert res_create["_id"] == "user_id_1"
    col.insert_one.assert_called()

@pytest.mark.asyncio
async def test_reviews_repo(mock_db_collections):
    col = mock_db_collections["reviews"]
    
    # 1. save_review
    col.insert_one.return_value = MagicMock(inserted_id="rev_id_1")
    review_data = {"summary": "Formatting smell", "issues": []}
    res = await reviews_repo.save_review("user_1", review_data)
    assert res["_id"] is not None
    assert isinstance(res["_id"], str)
    assert res["user_id"] == "user_1"

    # 2. get_review_by_id
    col.find_one.return_value = {"_id": "rev_id_1", "summary": "Smell"}
    res_get = await reviews_repo.get_review_by_id("rev_id_1")
    assert res_get["summary"] == "Smell"

@pytest.mark.asyncio
async def test_translations_repo(mock_db_collections):
    col = mock_db_collections["translations"]
    
    # 1. save_translation
    col.insert_one.return_value = MagicMock(inserted_id="trans_id_1")
    trans_data = {"translated_code": "System.out.println()"}
    res = await translations_repo.save_translation("user_1", trans_data)
    assert res["_id"] is not None
    assert isinstance(res["_id"], str)

    # 2. get_translation_by_id
    col.find_one.return_value = {"_id": "trans_id_1", "translated_code": "print()"}
    res_get = await translations_repo.get_translation_by_id("trans_id_1")
    assert res_get["translated_code"] == "print()"

@pytest.mark.asyncio
async def test_history_repo(mock_db_collections):
    col = mock_db_collections["history"]
    
    # 1. log_activity
    col.insert_one.return_value = MagicMock(inserted_id="log_id_1")
    res = await history_repo.log_activity("user_1", "review", "Reviewed main.py", {})
    assert res["_id"] is not None
    assert isinstance(res["_id"], str)
    assert res["type"] == "review"



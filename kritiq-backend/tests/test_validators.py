import pytest
from pydantic import ValidationError
from app.models.user_models import UserRegister, UserLogin
from app.models.review_models import ReviewRequest
from app.models.translation_models import TranslationRequest
from app.models.explanation_models import ExplanationRequest

def test_user_register_validators():
    # Valid model
    user = UserRegister(name="Test", email="test@example.com", password="securepassword123")
    assert user.name == "Test"
    
    # Weak password
    with pytest.raises(ValidationError):
        UserRegister(name="Test", email="test@example.com", password="weak")
        
    # Invalid email
    with pytest.raises(ValidationError):
        UserRegister(name="Test", email="invalid_email", password="securepassword123")

def test_review_request_validators():
    # Valid model
    req = ReviewRequest(code="def add(a, b): return a + b", language="python")
    assert req.language == "python"
    
    # Empty code
    with pytest.raises(ValidationError):
        ReviewRequest(code="   ", language="python")
        
    # Unsupported language
    with pytest.raises(ValidationError):
        ReviewRequest(code="def add(a, b): return a + b", language="cobol")

def test_translation_request_validators():
    # Valid model
    req = TranslationRequest(source_code="print('hello')", source_language="python", target_language="java")
    assert req.source_language == "python"
    assert req.target_language == "java"
    
    # Empty code
    with pytest.raises(ValidationError):
        TranslationRequest(source_code="", source_language="python", target_language="java")
        
    # Identical languages
    with pytest.raises(ValidationError):
        TranslationRequest(source_code="print('hello')", source_language="python", target_language="python")
        
    # Unsupported target language
    with pytest.raises(ValidationError):
        TranslationRequest(source_code="print('hello')", source_language="python", target_language="fortran")

def test_explanation_request_validators():
    # Valid model
    req = ExplanationRequest(code="x = 1", language="python")
    assert req.language == "python"
    
    # Empty code
    with pytest.raises(ValidationError):
        ExplanationRequest(code="  ", language="python")
        
    # Unsupported language
    with pytest.raises(ValidationError):
        ExplanationRequest(code="x = 1", language="pascal")

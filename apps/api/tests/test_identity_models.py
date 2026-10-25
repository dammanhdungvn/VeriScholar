"""Unit tests for Identity & Scholar Profile database models."""

from uuid import uuid4

from api.db.models.scholar_profile import ScholarProfileModel
from api.db.models.user import UserModel
from api.db.models.user_api_key import UserApiKeyModel


def test_user_model_defaults_and_fields():
    user = UserModel(
        email="scholar@univ.edu.vn",
        full_name="TS. Nguyễn Văn A",
        hashed_password="hashed_pw_example",
        role="researcher",
    )
    assert user.email == "scholar@univ.edu.vn"
    assert user.theme_preference == "system"
    assert user.byok_api_key_encrypted is None


def test_scholar_profile_and_user_model_instantiation():
    user = UserModel(
        email="scholar@stanford.edu",
        full_name="Dr. Jane Doe",
        hashed_password="secure_hashed_pw",
        role="researcher",
    )
    profile = ScholarProfileModel(
        user_id=user.id,
        institution="Stanford University",
        department="Computer Science",
        academic_rank="Associate Professor",
        orcid_id="0000-0002-1825-0097",
        research_interests=["Deep Learning", "NLP", "AI Agents"],
    )
    assert profile.user_id == user.id
    assert profile.institution == "Stanford University"
    assert "NLP" in profile.research_interests


def test_user_api_key_model_instantiation():
    user_id = uuid4()
    api_key = UserApiKeyModel(
        user_id=user_id,
        provider="openai",
        encrypted_key="enc_aes256gcm_secret",
        key_hint="sk-...a9b1",
        is_active=True,
    )
    assert api_key.user_id == user_id
    assert api_key.provider == "openai"
    assert api_key.is_active is True

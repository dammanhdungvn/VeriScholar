from uuid import uuid4

from core.domain.entities.user import UserEntity
from core.domain.value_objects.enums import AcademicRank, ThemePreference
from core.services.email_validator import (
    mask_api_key,
    validate_orcid_id,
)


def test_orcid_validation_regex():
    assert validate_orcid_id("0000-0002-1825-0097") is True
    assert validate_orcid_id("0000-0001-5109-370X") is True
    assert validate_orcid_id("invalid-orcid-1234") is False
    assert validate_orcid_id("0000-0002-1825") is False
    assert validate_orcid_id(None) is True  # Optional field


def test_mask_api_key_formats_correctly():
    assert mask_api_key("sk-proj-abcdef123456") == "sk-proj-...3456"
    assert mask_api_key("sk-short12") == "sk-...rt12"
    assert mask_api_key("") == ""


def test_user_entity_creation_and_theme_invariant():
    user = UserEntity(
        id=uuid4(),
        email="scholar@vnu.edu.vn",
        full_name="TS. Nguyễn Văn A",
        theme_preference=ThemePreference.DARK,
        academic_rank=AcademicRank.PHD,
        orcid_id="0000-0002-1825-0097",
    )
    assert user.theme_preference == ThemePreference.DARK
    assert user.academic_rank == AcademicRank.PHD
    assert user.email == "scholar@vnu.edu.vn"

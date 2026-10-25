from pathlib import Path
import pytest
from pydantic import ValidationError
from api.core.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_only_dev_prod_test_environments_allowed() -> None:
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="uat")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="staging")  # type: ignore[arg-type]


def test_default_model_and_langfuse_env_mapping() -> None:
    dev_settings = Settings(ENVIRONMENT="development", LANGFUSE_ENVIRONMENT="")
    prod_settings = Settings(ENVIRONMENT="production", LANGFUSE_ENVIRONMENT="")
    assert dev_settings.OPENAI_MODEL == "gpt-5.4-mini"
    assert dev_settings.LANGFUSE_MASK_INPUT_OUTPUT is False
    assert prod_settings.LANGFUSE_MASK_INPUT_OUTPUT is False


def test_bloat_files_and_models_removed() -> None:
    assert not (REPO_ROOT / "models").exists()
    assert not (REPO_ROOT / "apps/api/.env.uat").exists()
    assert not (REPO_ROOT / "deploy/docker-compose.enterprise.yml").exists()
    assert not (REPO_ROOT / "deploy/pgbouncer").exists()
    assert not (REPO_ROOT / "scripts/github_mcp_wrapper.sh").exists()
    assert not (REPO_ROOT / "temp").exists()
    assert not (REPO_ROOT / "tests").exists()

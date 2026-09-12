from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Automatically locate workspace root from file location
ROOT_DIR = Path(__file__).resolve().parents[3]


def get_default_reload_dirs() -> list[str]:
    """Dynamically resolves watch directories using absolute paths."""
    api_src = ROOT_DIR / "apps" / "api" / "src"
    core_src = ROOT_DIR / "packages" / "core" / "src"
    dirs: list[str] = []
    if api_src.exists():
        dirs.append(str(api_src))
    if core_src.exists():
        dirs.append(str(core_src))
    return dirs or ["src"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(ROOT_DIR / "apps" / "api" / ".env"),
            str(ROOT_DIR / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "VeriScholar API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD_DIRS: list[str] = Field(default_factory=get_default_reload_dirs)

    # Logging settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"

    # Database settings (PostgreSQL + pgvector)
    DATABASE_URL: str = "postgresql+asyncpg://verischolar:verischolar@localhost:5432/verischolar"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def assemble_async_db_url(cls, v: str) -> str:
        """Ensures asyncpg driver prefix is used for SQLAlchemy async engine."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    # LLM Inference Providers
    LLM_PROVIDER: Literal["docker-model-runner", "openai", "gemini", "ollama"] = (
        "docker-model-runner"
    )

    # Docker Model Runner settings
    DMR_BASE_URL: str = "http://localhost:12434/engines/llama.cpp/v1"
    DMR_MODEL: str = "ai/smollm2"

    # Cloud LLM Settings (SecretStr ensures no accidental leaks in logs/prints)
    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_MODEL: str = "gpt-5.6-luna"

    GEMINI_API_KEY: SecretStr | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()

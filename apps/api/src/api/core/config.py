from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_repo_root() -> Path:
    """Dynamically locates the monorepo root directory."""
    curr = Path(__file__).resolve()
    for parent in curr.parents:
        if (parent / "pnpm-workspace.yaml").exists() or (parent / "packages" / "core").exists():
            return parent
    return curr.parents[4]


# Monorepo Root Directory
ROOT_DIR = find_repo_root()


def get_default_reload_dirs() -> list[str]:
    """Dynamically resolves watch directories for uvicorn reloader."""
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

    # Storage settings (CAS Physical Blobs)
    STORAGE_DIR: Path = ROOT_DIR / "storage" / "blobs"

    # Logging settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"
    SQL_ECHO: bool = False

    # Authentication & JWT settings
    JWT_SECRET_KEY: str = "verischolar-super-secure-jwt-secret-key-2026-production-grade"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800  # 7 days

    # Langfuse AI Observability & Tracing settings
    LANGFUSE_ENABLED: bool = False
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: SecretStr | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_BASE_URL: str | None = None
    LANGFUSE_SAMPLE_RATE: float = 1.0
    LANGFUSE_MASK_INPUT_OUTPUT: bool = True
    LANGFUSE_ENVIRONMENT: str | None = None

    @model_validator(mode="after")
    def resolve_langfuse_settings(self) -> "Settings":
        """Synchronize LANGFUSE_BASE_URL with LANGFUSE_HOST and auto-enable if keys exist."""
        if self.LANGFUSE_BASE_URL:
            self.LANGFUSE_HOST = self.LANGFUSE_BASE_URL
        if self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY:
            # Auto-enable if keys are present and not explicitly set to false
            if "LANGFUSE_ENABLED" not in self.model_fields_set:
                self.LANGFUSE_ENABLED = True
        return self

    # Database settings (PostgreSQL + pgvector)
    DATABASE_URL: str = "postgresql+asyncpg://verischolar:verischolar@localhost:5432/verischolar"
    TEST_DATABASE_URL: str | None = None

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
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-5.6-luna"

    GEMINI_API_KEY: SecretStr | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()

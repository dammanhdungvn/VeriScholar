import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
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


def get_env_files() -> tuple[str, ...]:
    """Dynamically resolves environment configuration files with environment override precedence."""
    app_env = os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development"
    files = [
        str(ROOT_DIR / ".env"),
        str(ROOT_DIR / "apps" / "api" / ".env"),
        str(ROOT_DIR / f".env.{app_env}"),
        str(ROOT_DIR / "apps" / "api" / f".env.{app_env}"),
        ".env",
    ]
    for f in files:
        if Path(f).exists():
            load_dotenv(f, override=False)
    return tuple(files)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "VeriScholar API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD_DIRS: list[str] = Field(default_factory=get_default_reload_dirs)

    # Storage settings (CAS Physical Blobs & Rotating Logs)
    STORAGE_DIR: Path = ROOT_DIR / "storage" / "blobs"
    LOGS_DIR: Path = ROOT_DIR / "storage" / "logs"

    # Logging settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"
    SQL_ECHO: bool = False

    # Authentication & JWT settings
    JWT_SECRET_KEY: str = "verischolar-super-secure-jwt-secret-key-2026-production-grade"
    JWT_ALGORITHM: str = "HS256"
    BYOK_ENCRYPTION_KEY: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 7200  # 2 hours standard
    REMEMBER_ME_ACCESS_TOKEN_EXPIRE_SECONDS: int = 2592000  # 30 days for persistent session
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 7776000  # 90 days durable refresh
    GOOGLE_CLIENT_ID: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # SMTP & Email Delivery settings
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "onboarding@resend.dev"
    SMTP_FROM_NAME: str = "VeriScholar Academic Platform"
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"
    APP_PUBLIC_URL: str = "https://verischolar.duckdns.org"

    # Langfuse AI Observability & Tracing settings
    LANGFUSE_ENABLED: bool = False
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: SecretStr | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_BASE_URL: str | None = None
    LANGFUSE_SAMPLE_RATE: float = 1.0
    LANGFUSE_MASK_INPUT_OUTPUT: bool = False
    LANGFUSE_ENVIRONMENT: str | None = None

    # System Monitoring & Alerting settings
    SENTRY_DSN: str | None = None
    ALERT_WEBHOOK_URL: str | None = None
    E2B_LATEX_TEMPLATE: str = "base"

    # Reasoning Mode settings (5.6-luna)
    REASONING_EFFORT: Literal["low", "medium", "high"] = "medium"
    STREAM_REASONING_TOKENS: bool = True

    # Cohere Reranker settings
    COHERE_API_KEY: SecretStr | None = None
    COHERE_RERANK_MODEL: str = "rerank-v3.5"
    COHERE_RELEVANCE_THRESHOLD: float = 0.35

    # Azure Document Intelligence settings
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str | None = None
    AZURE_DOCUMENT_INTELLIGENCE_KEY: SecretStr | None = None

    @model_validator(mode="after")
    def resolve_langfuse_settings(self) -> "Settings":
        """Synchronize LANGFUSE_BASE_URL with LANGFUSE_HOST, auto-enable if keys exist,
        and set privacy defaults.
        """
        if self.LANGFUSE_BASE_URL:
            self.LANGFUSE_HOST = self.LANGFUSE_BASE_URL
        if self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY:
            # Auto-enable if keys exist and not explicitly set, except in test mode
            if "LANGFUSE_ENABLED" not in self.model_fields_set and self.ENVIRONMENT != "test":
                self.LANGFUSE_ENABLED = True
        if not self.LANGFUSE_ENVIRONMENT:
            if self.ENVIRONMENT == "development":
                self.LANGFUSE_ENVIRONMENT = "verischolar-dev"
            elif self.ENVIRONMENT == "production":
                self.LANGFUSE_ENVIRONMENT = "verischolar-prod"
            else:
                self.LANGFUSE_ENVIRONMENT = "test"
        if "LANGFUSE_MASK_INPUT_OUTPUT" not in self.model_fields_set:
            self.LANGFUSE_MASK_INPUT_OUTPUT = False
        return self

    @property
    def resolved_langfuse_environment(
        self,
    ) -> Literal["verischolar-dev", "verischolar-prod", "test"]:
        if self.ENVIRONMENT == "production":
            return "verischolar-prod"
        if self.ENVIRONMENT == "test":
            return "test"
        return "verischolar-dev"

    @model_validator(mode="after")
    def validate_azure_credentials(self) -> "Settings":
        """Heuristic guard: Auto-fix if Azure endpoint and key are accidentally swapped
        in configuration.
        """
        if (
            self.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
            and not self.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT.startswith(("http://", "https://"))
            and self.AZURE_DOCUMENT_INTELLIGENCE_KEY
            and self.AZURE_DOCUMENT_INTELLIGENCE_KEY.get_secret_value().startswith(
                ("http://", "https://")
            )
        ):
            swapped_endpoint = self.AZURE_DOCUMENT_INTELLIGENCE_KEY.get_secret_value()
            swapped_key = self.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
            self.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = swapped_endpoint
            self.AZURE_DOCUMENT_INTELLIGENCE_KEY = SecretStr(swapped_key)
        return self

    # Database settings (PostgreSQL + pgvector)
    DATABASE_URL: str = "postgresql+asyncpg://verischolar:verischolar@localhost:5432/verischolar"
    TEST_DATABASE_URL: str | None = None

    # Redis Cache & Background Tasks
    REDIS_URL: str = "redis://localhost:6379/0"

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
    OPENAI_MODEL: str = "gpt-5.4-mini"

    GEMINI_API_KEY: SecretStr | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Exa AI Neural Search Settings (Module 3)
    EXA_API_KEY: SecretStr | None = None

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()

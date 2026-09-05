"""
Centralized, environment-driven configuration.

All secrets and environment-specific values must come from environment
variables (loaded from `.env` in local development). Never hardcode
secrets here.
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "SocialGrowth AI"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / Auth ---
    JWT_SECRET_KEY: str = Field(default="CHANGE_ME_IN_ENV")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Database ---
    # Async URL used by the FastAPI app (asyncpg driver).
    DATABASE_URL: str = "postgresql+asyncpg://socialgrowth:socialgrowth@localhost:5432/socialgrowth"
    # Sync URL used by Alembic migrations (psycopg2 driver).
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://socialgrowth:socialgrowth@localhost:5432/socialgrowth"

    # --- Redis / Celery ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # --- Object storage (S3 / Cloudflare R2) ---
    S3_ENDPOINT_URL: str | None = None  # e.g. https://<accountid>.r2.cloudflarestorage.com
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str = "socialgrowth-assets"
    S3_REGION: str = "auto"
    S3_PUBLIC_BASE_URL: str | None = None  # CDN/public URL prefix for served assets

    # --- AI providers (abstracted; see app/ai/providers) ---
    LLM_PROVIDER: str = "mock"  # mock | openai | anthropic
    IMAGE_PROVIDER: str = "mock"  # mock | gemini | openai | stability
    VIDEO_PROVIDER: str = "mock"  # mock | gemini
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    STABILITY_API_KEY: str | None = None

    # Gemini (Google AI) — powers IMAGE_PROVIDER=gemini and VIDEO_PROVIDER=gemini.
    # Get a key at https://aistudio.google.com/apikey. Video generation (Veo) is
    # a paid, metered API with no free tier; image generation has a free tier.
    GEMINI_API_KEY: str | None = None
    GEMINI_IMAGE_MODEL: str = "gemini-2.5-flash-image"  # "Nano Banana"; or an imagen-*.0-generate-* id
    GEMINI_VIDEO_MODEL: str = "veo-3.1-fast-generate-preview"  # cheapest current Veo tier

    # --- Social platform OAuth (Phase 3) ---
    META_APP_ID: str | None = None
    META_APP_SECRET: str | None = None
    LINKEDIN_CLIENT_ID: str | None = None
    LINKEDIN_CLIENT_SECRET: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # --- Observability ---
    SENTRY_DSN: str | None = None
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

"""
Central configuration. Every external integration key lives here and is
read from environment variables — nothing is hardcoded.

For local dev, copy `.env.example` to `.env` and fill in the values.
For Railway, set these as Service Variables in the dashboard.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Core app ---
    ENV: str = "development"
    APP_NAME: str = "SmartPrepAI"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Database (Railway provisions this automatically as DATABASE_URL) ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/smartprepai"
    REDIS_URL: str = "redis://localhost:6379/0"

    # =========================================================================
    # INTEGRATION POINT #1 — MyQuest API (past questions provider)
    # Sign up / get credentials from MyQuest, then set these two values.
    # Until MYQUEST_API_KEY is set, the platform automatically falls back to
    # the local `questions` table (seeded with sample WAEC/JAMB data) so the
    # mock-test engine still works end to end during development.
    # =========================================================================
    MYQUEST_API_KEY: str = ""
    MYQUEST_BASE_URL: str = "https://api.myquest.example.com"  # TODO: replace with real base URL

    # =========================================================================
    # INTEGRATION POINT #2 — Paystack (payments)
    # https://dashboard.paystack.com/#/settings/developer
    # =========================================================================
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    PAYSTACK_WEBHOOK_URL: str = ""  # informational only, set in Paystack dashboard

    # =========================================================================
    # INTEGRATION POINT #3 — Groq (free/fast LLM inference for the tutor)
    # https://console.groq.com/keys
    # =========================================================================
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # =========================================================================
    # INTEGRATION POINT #4 — Qdrant (open-source vector DB, replaces Pinecone)
    # Deploy via Railway's 1-click Qdrant template, then copy the URL + key.
    # =========================================================================
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "smartprepai_textbooks"

    # Embedding model — BAAI/bge-m3 (open source, runs locally on the backend).
    # Swap to BAAI/bge-small-en-v1.5 if you need a lighter footprint on a
    # small Railway instance (384-dim vs bge-m3's 1024-dim).
    EMBEDDING_MODEL: str = "BAAI/bge-m3"


settings = Settings()

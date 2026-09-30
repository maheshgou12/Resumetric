from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import field_validator
from typing import Annotated, List
import json
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Resume Analyzer Pro"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-use-256-bit-random"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_analyzer"

    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@resumeanalyzerpro.com"
    EMAIL_FROM_NAME: str = "Resume Analyzer Pro"

    # Email via Gmail SMTP (delivers to ANY inbox, no domain needed).
    # Create an App Password at myaccount.google.com/apppasswords (needs 2-Step Verification).
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = ""
    SMTP_APP_PASSWORD: str = ""

    # AWS S3 / Cloudflare R2
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "resume-analyzer"
    S3_REGION: str = "auto"
    S3_ENDPOINT_URL: str = ""  # For R2: https://ACCOUNT_ID.r2.cloudflarestorage.com

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # CORS — comma-separated env overrides defaults (set this in Render to your Vercel URL)
    ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://resume-analyzer-pro.vercel.app",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(o).strip() for o in parsed if str(o).strip()]
                except Exception:
                    pass
            return [o.strip() for o in s.split(",") if o.strip()]
        return v

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:5173"

    # File Uploads
    MAX_UPLOAD_SIZE_MB: int = 5

    # Rate Limiting (kept for compatibility — analyses are unlimited, not enforced)
    FREE_TIER_ANALYSES_PER_MONTH: int = 0

    # Sentry
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()

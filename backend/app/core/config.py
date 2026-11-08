from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import field_validator
from typing import Annotated, List
import json
import os


from pathlib import Path

_ENV_PATHS = (
    str(Path(__file__).resolve().parent.parent.parent / ".env"),
    ".env",
)


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Resume Analyzer Pro"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-use-256-bit-random"

    # Database (Defaults to zero-setup SQLite for local dev; set to Postgres in production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./careerlens.db"

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

    # Email via Brevo HTTPS API (delivers to ANY inbox, no domain needed,
    # works on hosts that block SMTP ports). Sender must be verified in Brevo.
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""

    # Email via Gmail SMTP (delivers to ANY inbox, no domain needed).
    # Create an App Password at myaccount.google.com/apppasswords (needs 2-Step Verification).
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME") or "maheshburra2712@gmail.com"
    SMTP_APP_PASSWORD: str = os.getenv("SMTP_APP_PASSWORD") or "iocq hdqz xsio ztmx"

    # AWS S3 / Cloudflare R2
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "resume-analyzer"
    S3_REGION: str = "auto"
    S3_ENDPOINT_URL: str = ""  # For R2: https://ACCOUNT_ID.r2.cloudflarestorage.com

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "qwen/qwen3.8-27b"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # CORS — comma-separated env overrides defaults (set this in Render to your Vercel URL)
    ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://resumetric-1.onrender.com",
        "https://resumetric-challengers13.vercel.app",
        "https://resume-analyzer-pro.vercel.app",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        origins = []
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        origins = [str(o).strip() for o in parsed if str(o).strip()]
                except Exception:
                    pass
            if not origins:
                origins = [o.strip() for o in s.split(",") if o.strip()]
        elif isinstance(v, list):
            origins = list(v)

        for default_url in ("https://resumetric-1.onrender.com", os.environ.get("RENDER_EXTERNAL_URL")):
            if default_url and default_url not in origins:
                origins.append(default_url)
        return origins

    # Frontend URL (for email links)
    FRONTEND_URL: str = "https://resumetric-1.onrender.com"

    @field_validator("FRONTEND_URL", mode="before")
    @classmethod
    def _resolve_frontend_url(cls, v):
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url.rstrip("/")
        if v and not v.startswith("http://localhost"):
            return v.rstrip("/")
        return "https://resumetric-1.onrender.com"

    # File Uploads
    MAX_UPLOAD_SIZE_MB: int = 5

    # Rate Limiting (kept for compatibility — analyses are unlimited, not enforced)
    FREE_TIER_ANALYSES_PER_MONTH: int = 0

    # Sentry
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(env_file=_ENV_PATHS, case_sensitive=True, extra="ignore")


settings = Settings()

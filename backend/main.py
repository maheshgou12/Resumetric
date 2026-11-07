"""
Resume Analyzer Pro - FastAPI Backend
"""
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Auto-seed default admin on fresh database so production is immediately ready
    try:
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.models import User, UserRole
        from app.core.security import get_password_hash
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).limit(1))
            if not result.scalar_one_or_none():
                admin = User(
                    email="admin@careerlens.ai",
                    full_name="Admin User",
                    hashed_password=get_password_hash("Admin@12345"),
                    role=UserRole.admin,
                    is_verified=True,
                )
                session.add(admin)
                await session.commit()
    except Exception:
        pass

    yield
    # Shutdown
    await engine.dispose()


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
    )

app = FastAPI(
    title="CareerLens AI API",
    version="2.0.0",
    description="CareerLens AI — resume scoring, career domains, skill gaps, roadmaps, interview prep",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """Landing endpoint so browsers don't see `{"detail": "Not Found"}`."""
    return {
        "app": "CareerLens AI API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

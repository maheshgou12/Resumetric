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


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

# Locate frontend production build directory if present
DIST_DIRS = [
    Path(__file__).resolve().parent.parent / "frontend" / "dist",
    Path(__file__).resolve().parent / "dist",
    Path("/app/frontend/dist"),
    Path("/app/dist"),
]
dist_dir = next((d for d in DIST_DIRS if d.is_dir() and (d / "index.html").is_file()), None)

if dist_dir:
    assets_dir = dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path in ("health", "docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = dist_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")
else:
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

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.career import router as career_router
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(career_router, prefix="/career", tags=["CareerLens"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

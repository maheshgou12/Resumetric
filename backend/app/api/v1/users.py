"""
User profile management routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.models import User, Analysis

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    dark_mode: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
        "avatar_url": current_user.avatar_url,
        "dark_mode": current_user.dark_mode,
        "analyses_this_month": current_user.analyses_this_month,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.patch("/me")
async def update_profile(
    body: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.full_name is not None:
        current_user.full_name = body.full_name.strip()
    if body.dark_mode is not None:
        current_user.dark_mode = body.dark_mode
    await db.commit()
    return {"message": "Profile updated"}


@router.post("/me/change-password")
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.hashed_password:
        raise HTTPException(status_code=400, detail="Cannot change password for OAuth accounts")
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    current_user.hashed_password = get_password_hash(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's analytics stats for dashboard"""
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
        .limit(50)
    )
    analyses = result.scalars().all()

    completed = [a for a in analyses if a.match_score is not None]
    avg_match = sum(a.match_score for a in completed) / len(completed) if completed else 0
    avg_ats = sum(a.ats_score for a in completed if a.ats_score) / len(completed) if completed else 0

    # Trend data for chart (last 10 analyses)
    trend = [
        {
            "date": a.created_at.strftime("%b %d") if a.created_at else "",
            "match_score": round(a.match_score, 1) if a.match_score else 0,
            "ats_score": round(a.ats_score, 1) if a.ats_score else 0,
        }
        for a in reversed(completed[:10])
    ]

    return {
        "total_analyses": len(analyses),
        "completed_analyses": len(completed),
        "avg_match_score": round(avg_match, 1),
        "avg_ats_score": round(avg_ats, 1),
        "best_match_score": max((a.match_score for a in completed), default=0),
        "analyses_this_month": current_user.analyses_this_month,
        "monthly_limit": settings.FREE_TIER_ANALYSES_PER_MONTH,
        "trend": trend,
    }

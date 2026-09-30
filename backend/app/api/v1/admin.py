"""
Admin analytics dashboard routes (role-gated).
DB-portable: no Postgres-only SQL (works on SQLite + Postgres).
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from collections import Counter, defaultdict

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.models import User, Analysis, AnalysisStatus

router = APIRouter()

VALID_STATUSES = {s.value for s in AnalysisStatus}


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Overall platform statistics"""
    # Total users
    user_count = await db.execute(select(func.count(User.id)))
    total_users = user_count.scalar()

    # Total analyses
    analysis_count = await db.execute(select(func.count(Analysis.id)))
    total_analyses = analysis_count.scalar()

    # Avg scores
    scores = await db.execute(
        select(func.avg(Analysis.match_score), func.avg(Analysis.ats_score))
        .where(Analysis.status == AnalysisStatus.completed)
    )
    avg_match, avg_ats = scores.one()

    # New users last 30 days (portable: Python-computed cutoff, not NOW()/INTERVAL)
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= cutoff)
    )
    new_users_30d = new_users_result.scalar()

    return {
        "total_users": total_users,
        "total_analyses": total_analyses,
        "avg_match_score": round(float(avg_match or 0), 1),
        "avg_ats_score": round(float(avg_ats or 0), 1),
        "new_users_30d": new_users_30d,
    }


@router.get("/missing-skills")
async def get_top_missing_skills(
    limit: int = 15,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Most common missing skills across all analyses"""
    result = await db.execute(
        select(Analysis.missing_skills).where(
            Analysis.missing_skills.isnot(None),
            Analysis.status == AnalysisStatus.completed,
        ).limit(500)
    )
    all_missing = result.scalars().all()

    counter = Counter()
    for skills_list in all_missing:
        if skills_list:
            for skill in skills_list:
                counter[skill] += 1

    top = [{"skill": s, "count": c} for s, c in counter.most_common(limit)]
    return top


@router.get("/signup-trend")
async def get_signup_trend(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Daily signups for the last N days (grouped in Python — portable)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(User.created_at).where(User.created_at >= cutoff)
    )
    per_day: dict[str, int] = defaultdict(int)
    for (created_at,) in result.all():
        if created_at:
            day = created_at.strftime("%Y-%m-%d") if hasattr(created_at, "strftime") else str(created_at)[:10]
            per_day[day] += 1
    return [{"date": d, "signups": per_day[d]} for d in sorted(per_day)]


@router.get("/analyses")
async def list_all_analyses(
    skip: int = 0,
    limit: int = 50,
    search: str = Query(default=""),
    status_filter: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Searchable/sortable analyses table for admin"""
    query = (
        select(Analysis, User.email, User.full_name)
        .join(User, Analysis.user_id == User.id)
        .order_by(desc(Analysis.created_at))
    )
    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%"))
            | (User.full_name.ilike(f"%{search}%"))
            | (Analysis.job_title.ilike(f"%{search}%"))
        )
    if status_filter:
        if status_filter not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {sorted(VALID_STATUSES)}")
        query = query.where(Analysis.status == AnalysisStatus(status_filter))

    result = await db.execute(query.offset(skip).limit(limit))
    rows = result.all()

    return [
        {
            "id": str(row[0].id),
            "user_email": row[1],
            "user_name": row[2],
            "job_title": row[0].job_title,
            "company_name": row[0].company_name,
            "status": row[0].status.value,
            "match_score": row[0].match_score,
            "ats_score": row[0].ats_score,
            "created_at": row[0].created_at.isoformat() if row[0].created_at else None,
        }
        for row in rows
    ]


@router.get("/users")
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    search: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Admin user list"""
    query = select(User).order_by(desc(User.created_at))
    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%"))
            | (User.full_name.ilike(f"%{search}%"))
        )
    result = await db.execute(query.offset(skip).limit(limit))
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_verified": u.is_verified,
            "is_active": u.is_active,
            "analyses_this_month": u.analyses_this_month,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]

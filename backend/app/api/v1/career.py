"""
CareerLens AI — Resume management + Career intelligence routes.
Covers: multi-resume upload/view/delete/download/compare/re-analyze,
100-pt score, domains, job compare, roadmaps, interview prep, progress.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func as sa_func
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.models import Resume, Analysis, User
from app.services.resume_parser import extract_text, extract_entities
from app.services.career_service import (
    compute_resume_score, suggest_career_domains, compare_with_job,
    roadmap_for_skill, interview_questions, diff_texts,
)
from app.services.analysis_engine import (
    COMMON_SKILLS, compute_match_score, compute_ats_score, detect_skills,
)

router = APIRouter()
ALLOWED = {"application/pdf",
           "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
           "application/msword"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _resume_to_dict(r: Resume) -> dict:
    return {
        "id": str(r.id), "name": r.name, "version": r.version,
        "target_role": r.target_role, "filename": r.filename,
        "entities": r.entities, "resume_score": r.resume_score,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "words": len((r.content or "").split()),
    }


# ─── Resume CRUD + versions ──────────────────────────────────────────────

class CompareReq(BaseModel):
    resume_a_id: str
    resume_b_id: str


@router.post("/resumes", status_code=201)
async def upload_resume(
    resume: UploadFile = File(...),
    name: str = Form(default=""),
    target_role: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if resume.content_type not in ALLOWED and not (resume.filename or "").endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(400, "Only PDF and DOCX supported")
    blob = await resume.read()
    if len(blob) > MAX_SIZE:
        raise HTTPException(400, f"Max {settings.MAX_UPLOAD_SIZE_MB}MB")
    try:
        text = extract_text(blob, resume.content_type or "", resume.filename or "")
    except Exception as e:
        raise HTTPException(400, f"Parse failed: {e}")
    if len(text.strip()) < 50:
        raise HTTPException(400, "Not enough text extracted (image-only scan?)")
    entities = extract_entities(text)
    score = compute_resume_score(text, entities)

    # version = count of same-name resumes + 1
    label = name.strip() or (resume.filename or "Resume")
    q = await db.execute(select(sa_func.count(Resume.id)).where(
        Resume.user_id == current_user.id, Resume.name == label))
    version = (q.scalar() or 0) + 1

    r = Resume(user_id=current_user.id, name=label, version=version,
               target_role=target_role or None, filename=resume.filename,
               content=text, entities=entities, resume_score=score)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return _resume_to_dict(r)


@router.get("/resumes")
async def list_resumes(db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Resume).where(
        Resume.user_id == current_user.id).order_by(desc(Resume.created_at)))
    return [_resume_to_dict(r) for r in res.scalars().all()]


@router.post("/resumes/compare")
async def compare_resumes(body: CompareReq, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    async def _get(rid: str) -> Resume:
        r = (await db.execute(select(Resume).where(
            Resume.id == rid, Resume.user_id == current_user.id))).scalar_one_or_none()
        if not r:
            raise HTTPException(404, f"Resume {rid} not found")
        return r
    a, b = await _get(body.resume_a_id), await _get(body.resume_b_id)
    d = diff_texts(a.content or "", b.content or "")
    sa = (a.resume_score or {}).get("overall", 0)
    sb = (b.resume_score or {}).get("overall", 0)
    skills_a = set((a.entities or {}).get("skills", []))
    skills_b = set((b.entities or {}).get("skills", []))
    return {
        "a": {"id": str(a.id), "name": a.name, "version": a.version, "score": sa},
        "b": {"id": str(b.id), "name": b.name, "version": b.version, "score": sb},
        "score_delta": round(sb - sa, 1),
        "text_diff": d,
        "skills_added": sorted(skills_b - skills_a),
        "skills_removed": sorted(skills_a - skills_b),
        "verdict": f"{b.name} v{b.version} scores {sb}/100 vs {sa}/100",
    }


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: str, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    r = (await db.execute(select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Resume not found")
    d = _resume_to_dict(r)
    d["content_preview"] = (r.content or "")[:2000]
    return d


@router.get("/resumes/{resume_id}/download", response_class=PlainTextResponse)
async def download_resume(resume_id: str, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    r = (await db.execute(select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Resume not found")
    return r.content or ""


@router.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    r = (await db.execute(select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Resume not found")
    await db.delete(r)
    await db.commit()
    return {"message": "Resume deleted"}


@router.post("/resumes/{resume_id}/reanalyze")
async def reanalyze_resume(resume_id: str, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    r = (await db.execute(select(Resume).where(
        Resume.id == resume_id, Resume.user_id == current_user.id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Resume not found")
    entities = extract_entities(r.content or "")
    score = compute_resume_score(r.content or "", entities)
    r.entities = entities
    r.resume_score = score
    await db.commit()
    return _resume_to_dict(r)


# ─── Standalone analysis (auth required, abuse-capped) ───────────────────
MAX_TEXT_LEN = 20000

class ScoreReq(BaseModel):
    resume_text: str


@router.post("/score")
async def standalone_score(
    body: ScoreReq,
    current_user: User = Depends(get_current_user),
):
    text = (body.resume_text or "").strip()
    if len(text) < 50:
        raise HTTPException(400, "Resume text too short")
    if len(text) > MAX_TEXT_LEN:
        raise HTTPException(400, f"Resume text too long (max {MAX_TEXT_LEN} chars)")
    entities = extract_entities(text)
    score = compute_resume_score(text, entities)
    domains = suggest_career_domains(entities.get("skills", []))
    return {"entities": entities, "score": score, "career_domains": domains}


@router.get("/domains")
async def career_domains(
    skills: str = "",
    current_user: User = Depends(get_current_user),
):
    if len(skills) > 2000:
        raise HTTPException(400, "Skills query too long")
    skill_list = [s.strip() for s in skills.split(",") if s.strip()][:50]
    return {"domains": suggest_career_domains(skill_list, top_n=5)}


class JobCompareReq(BaseModel):
    resume_text: str
    job_description: str


@router.post("/job-compare")
async def job_compare(
    body: JobCompareReq,
    current_user: User = Depends(get_current_user),
):
    resume_text = (body.resume_text or "").strip()
    jd = (body.job_description or "").strip()
    if len(resume_text) < 50:
        raise HTTPException(400, "Resume text too short")
    if len(resume_text) > MAX_TEXT_LEN or len(jd) > MAX_TEXT_LEN:
        raise HTTPException(400, f"Input too long (max {MAX_TEXT_LEN} chars each)")
    if len(jd) < 20:
        raise HTTPException(400, "Job description too short")
    entities = extract_entities(resume_text)
    gap = compare_with_job(entities.get("skills", []), jd, COMMON_SKILLS)
    match = compute_match_score(resume_text, jd)
    ats, issues = compute_ats_score(resume_text, jd)
    matched, missing = detect_skills(resume_text, jd)
    return {"match_score": match, "ats_score": ats, "ats_issues": issues,
            "gap": gap, "matched": matched, "missing": missing,
            "roadmap": [roadmap_for_skill(s) for s in missing[:5]]}


@router.get("/roadmap/{skill}")
async def skill_roadmap(
    skill: str,
    current_user: User = Depends(get_current_user),
):
    skill = (skill or "").strip()[:100]
    if not skill:
        raise HTTPException(400, "Skill required")
    return roadmap_for_skill(skill)


class InterviewReq(BaseModel):
    domain: str = "Backend Development"
    skills: str = ""


ALLOWED_DOMAINS = {
    "Backend Development", "Frontend Development", "Full-Stack Development",
    "Data Science / ML", "Data Analytics", "DevOps / Cloud",
    "Mobile Development", "Cybersecurity", "UI/UX Design", "QA / Testing",
}


@router.post("/interview-prep")
async def interview_prep(
    body: InterviewReq,
    current_user: User = Depends(get_current_user),
):
    domain = (body.domain or "").strip()[:100] or "Backend Development"
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(400, f"Unknown domain. Choose from: {sorted(ALLOWED_DOMAINS)}")
    if len(body.skills or "") > 2000:
        raise HTTPException(400, "Skills too long")
    skill_list = [s.strip() for s in body.skills.split(",") if s.strip()][:30]
    return {"domain": domain,
            "questions": interview_questions(domain, skill_list)}


@router.get("/progress")
async def progress(db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Analysis).where(
        Analysis.user_id == current_user.id).order_by(Analysis.created_at))
    rows = res.scalars().all()[-100:]
    trend = [{"date": (a.created_at.isoformat() if a.created_at else ""),
              "match": a.match_score, "ats": a.ats_score} for a in rows]
    res2 = await db.execute(select(Resume).where(
        Resume.user_id == current_user.id).order_by(Resume.created_at))
    rws = res2.scalars().all()[-100:]
    rtrend = [{"name": r.name, "version": r.version,
               "score": (r.resume_score or {}).get("overall", 0)} for r in rws]
    return {"analyses": len(rows), "resumes": len(rws),
            "match_trend": trend, "resume_trend": rtrend}

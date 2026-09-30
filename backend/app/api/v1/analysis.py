"""
Resume Analysis API routes
"""
from typing import Optional
import uuid
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form,
    BackgroundTasks, status
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_verified_user
from app.core.config import settings
from app.models.models import Analysis, AnalysisStatus, User
from app.services.resume_parser import extract_text, extract_entities
from app.services.analysis_engine import (
    compute_match_score, compute_ats_score, detect_skills,
    generate_llm_feedback, generate_skill_roadmap
)
from app.services.career_service import compute_resume_score, suggest_career_domains
from app.services.pdf_generator import generate_pdf_report
from app.services.storage_service import upload_file, upload_pdf_report, get_presigned_url
from app.services.email_service import send_analysis_report_email

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _celery_available() -> bool:
    """1s TCP ping of the Celery broker. False in local SQLite mode (no Redis),
    so we skip .delay() which would otherwise block retrying the connection."""
    import socket
    from urllib.parse import urlparse
    try:
        u = urlparse(settings.CELERY_BROKER_URL)
        sock = socket.create_connection((u.hostname or "localhost", u.port or 6379), timeout=1)
        sock.close()
        return True
    except Exception:
        return False


def analysis_to_dict(analysis: Analysis) -> dict:
    return {
        "id": str(analysis.id),
        "status": analysis.status.value,
        "resume_filename": analysis.resume_filename,
        "job_title": analysis.job_title,
        "company_name": analysis.company_name,
        "match_score": analysis.match_score,
        "ats_score": analysis.ats_score,
        "matched_skills": analysis.matched_skills,
        "missing_skills": analysis.missing_skills,
        "extracted_entities": analysis.extracted_entities,
        "feedback": analysis.feedback,
        "skill_roadmap": analysis.skill_roadmap,
        "report_url": analysis.report_url,
        "report_emailed": analysis.report_emailed,
        "error_message": analysis.error_message,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


async def _run_analysis_inline(analysis_id: str, user_id: str):
    """Run analysis in background (fallback when Celery is not available).

    Uses its OWN database session: the request's session is already
    closed by the time background tasks run, so re-fetch rows by id.
    The blocking Groq HTTP call runs in a thread to keep the event
    loop (and status polling) responsive.
    """
    import asyncio
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis = result.scalar_one_or_none()
            if not analysis:
                return
            uresult = await db.execute(select(User).where(User.id == user_id))
            user = uresult.scalar_one_or_none()

            analysis.status = AnalysisStatus.processing
            await db.commit()

            match_score = compute_match_score(analysis.resume_text, analysis.job_description)
            ats_score, ats_issues = compute_ats_score(analysis.resume_text)
            matched_skills, missing_skills = detect_skills(analysis.resume_text, analysis.job_description)

            feedback = await asyncio.to_thread(
                generate_llm_feedback,
                analysis.resume_text, analysis.job_description,
                match_score, ats_score, matched_skills, missing_skills,
            )
            roadmap = generate_skill_roadmap(missing_skills)

            # CareerLens 100-pt standalone score + domain suggestions (offline, no extra LLM cost)
            try:
                stored_entities = analysis.extracted_entities or {}
                career_score = compute_resume_score(analysis.resume_text, stored_entities)
                career_domains = suggest_career_domains(stored_entities.get("skills", []))
            except Exception:
                career_score, career_domains = None, []

            analysis.match_score = match_score
            analysis.ats_score = ats_score
            analysis.matched_skills = matched_skills
            analysis.missing_skills = missing_skills
            analysis.feedback = {**feedback, "ats_issues": ats_issues,
                                 "resume_score": career_score, "career_domains": career_domains}
            analysis.skill_roadmap = roadmap

            # Generate and upload PDF
            if user:
                pdf_bytes = generate_pdf_report(
                    user_name=user.full_name,
                    user_email=user.email,
                    resume_filename=analysis.resume_filename or "resume",
                    job_description_preview=analysis.job_description[:200],
                    match_score=match_score,
                    ats_score=ats_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    feedback=feedback,
                    skill_roadmap=roadmap,
                    analysis_id=str(analysis.id),
                )
                report_key = upload_pdf_report(pdf_bytes, str(analysis.id))
                if report_key:
                    analysis.report_s3_key = report_key
                    report_url = get_presigned_url(report_key, expires_in=86400 * 7)
                    analysis.report_url = report_url
                    try:
                        sent = send_analysis_report_email(
                            user.email, user.full_name, report_url or "", match_score, ats_score
                        )
                        analysis.report_emailed = sent
                    except Exception:
                        pass

            analysis.status = AnalysisStatus.completed
            await db.commit()

        except Exception as e:
            try:
                result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
                failed = result.scalar_one_or_none()
                if failed:
                    failed.status = AnalysisStatus.failed
                    failed.error_message = str(e)
                    await db.commit()
            except Exception:
                pass


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_analysis(
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: str = Form(default=""),
    company_name: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload resume + JD, kick off analysis"""

    # Validate file type
    if resume.content_type not in ALLOWED_TYPES:
        # Try by extension
        filename = resume.filename or ""
        if not (filename.endswith(".pdf") or filename.endswith(".docx") or filename.endswith(".doc")):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported"
            )

    # Read and validate size
    file_content = await resume.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    # Rate limiting check
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if (
        current_user.analyses_month_reset is None
        or current_user.analyses_month_reset.replace(tzinfo=timezone.utc).month != now.month
    ):
        current_user.analyses_this_month = 0
        current_user.analyses_month_reset = now

    if (
        current_user.role.value != "admin"
        and current_user.analyses_this_month >= settings.FREE_TIER_ANALYSES_PER_MONTH
    ):
        raise HTTPException(
            status_code=429,
            detail=f"Monthly analysis limit ({settings.FREE_TIER_ANALYSES_PER_MONTH}) reached. Upgrade to continue."
        )

    # Extract text
    try:
        resume_text = extract_text(file_content, resume.content_type or "", resume.filename or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract text from file: {str(e)}")

    if len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract sufficient text from resume. Please ensure it's not a scanned image.")

    # Extract entities
    entities = extract_entities(resume_text)

    # Upload resume to S3
    s3_key = upload_file(file_content, resume.filename or "resume.pdf", resume.content_type or "application/pdf")

    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        resume_filename=resume.filename,
        resume_s3_key=s3_key,
        resume_text=resume_text,
        job_description=job_description,
        job_title=job_title or None,
        company_name=company_name or None,
        extracted_entities=entities,
        status=AnalysisStatus.pending,
    )
    db.add(analysis)

    # Increment usage counter
    current_user.analyses_this_month += 1
    await db.commit()
    await db.refresh(analysis)

    # Try Celery, fall back to BackgroundTasks
    # NOTE: .delay() blocks retrying when the Redis broker is down (local
    # SQLite mode has no Redis), so ping the broker first with a 1s timeout.
    # IDs (plain strings) are passed — the task opens its own DB session.
    analysis_id = str(analysis.id)
    user_id = str(current_user.id)
    if _celery_available():
        try:
            from app.celery_tasks import run_analysis_task
            run_analysis_task.delay(analysis_id)
        except Exception:
            background_tasks.add_task(_run_analysis_inline, analysis_id, user_id)
    else:
        background_tasks.add_task(_run_analysis_inline, analysis_id, user_id)

    return analysis_to_dict(analysis)


@router.get("/")
async def list_analyses(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's analysis history"""
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
        .offset(skip)
        .limit(limit)
    )
    analyses = result.scalars().all()
    return [analysis_to_dict(a) for a in analyses]


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific analysis result"""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_to_dict(analysis)


@router.get("/{analysis_id}/report-url")
async def get_report_url(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a fresh presigned URL for the report"""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if not analysis.report_s3_key:
        raise HTTPException(status_code=404, detail="Report not available yet")

    url = get_presigned_url(analysis.report_s3_key, expires_in=3600)
    return {"url": url}


@router.get("/{analysis_id}/report")
async def download_report(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the PDF report, regenerated on demand from stored results.

    Works everywhere — including local mode with no S3 bucket configured.
    """
    import io
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.status != AnalysisStatus.completed:
        raise HTTPException(status_code=409, detail="Analysis is not completed yet")

    feedback = analysis.feedback or {}
    pdf_bytes = generate_pdf_report(
        user_name=current_user.full_name,
        user_email=current_user.email,
        resume_filename=analysis.resume_filename or "resume",
        job_description_preview=(analysis.job_description or "")[:200],
        match_score=analysis.match_score or 0,
        ats_score=analysis.ats_score or 0,
        matched_skills=analysis.matched_skills or [],
        missing_skills=analysis.missing_skills or [],
        feedback=feedback,
        skill_roadmap=analysis.skill_roadmap or [],
        analysis_id=str(analysis.id),
    )
    filename = f"careerlens-report-{str(analysis.id)[:8]}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


@router.post("/{analysis_id}/chat")
async def ai_chat(
    analysis_id: str,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI rewrite assistant chat"""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    from groq import Groq
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")

    client = Groq(api_key=settings.GROQ_API_KEY)
    system_prompt = f"""You are an expert resume writer and career coach helping improve a resume.
The resume is targeting: {analysis.job_title or 'the provided job description'}.
Match score: {analysis.match_score}% | ATS score: {analysis.ats_score}%

Resume excerpt (first 1000 chars): {(analysis.resume_text or '')[:1000]}

Job Description excerpt (first 500 chars): {analysis.job_description[:500]}

Help the user improve their resume with specific, actionable suggestions. Be concise and direct."""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": body.message},
        ],
        temperature=0.7,
        max_tokens=800,
    )
    return {"reply": response.choices[0].message.content}


@router.post("/{analysis_id}/cover-letter")
async def generate_cover_letter(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a tailored cover letter"""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")

    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""Write a professional, personalized cover letter for this candidate.

Candidate Name: {current_user.full_name}
Target Role: {analysis.job_title or 'the position'}
Company: {analysis.company_name or 'the company'}
Matched Skills: {', '.join((analysis.matched_skills or [])[:8])}

Resume Summary (first 800 chars): {(analysis.resume_text or '')[:800]}
Job Description (first 800 chars): {analysis.job_description[:800]}

Write a compelling 3-4 paragraph cover letter. Make it specific, not generic.
Start with Dear Hiring Manager, and end with Sincerely, {current_user.full_name}."""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1000,
    )
    return {"cover_letter": response.choices[0].message.content}

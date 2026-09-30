"""
Celery app and task definitions
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "resume_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.celery_tasks.run_analysis": {"queue": "analysis"},
        "app.celery_tasks.send_report_email": {"queue": "email"},
    },
)


@celery_app.task(bind=True, max_retries=3)
def run_analysis_task(self, analysis_id: str):
    """
    Background task: run full AI analysis for a given analysis_id
    """
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.models.models import Analysis, AnalysisStatus, User
    from app.services.analysis_engine import (
        compute_match_score, compute_ats_score, detect_skills,
        generate_llm_feedback, generate_skill_roadmap
    )
    from app.services.pdf_generator import generate_pdf_report
    from app.services.storage_service import upload_pdf_report, get_presigned_url
    from app.services.email_service import send_analysis_report_email
    from sqlalchemy import select
    import uuid

    async def _run():
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

        async with AsyncSession() as session:
            # Fetch analysis
            result = await session.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()
            if not analysis:
                return

            # Fetch user
            user_result = await session.execute(
                select(User).where(User.id == analysis.user_id)
            )
            user = user_result.scalar_one_or_none()

            try:
                analysis.status = AnalysisStatus.processing
                await session.commit()

                # Run scoring
                match_score = compute_match_score(analysis.resume_text, analysis.job_description)
                ats_score, ats_issues = compute_ats_score(analysis.resume_text, analysis.job_description)
                matched_skills, missing_skills = detect_skills(analysis.resume_text, analysis.job_description)

                # LLM feedback
                feedback = generate_llm_feedback(
                    analysis.resume_text, analysis.job_description,
                    match_score, ats_score, matched_skills, missing_skills
                )

                # Skill roadmap
                roadmap = generate_skill_roadmap(missing_skills)

                # CareerLens 100-pt standalone score + domains
                try:
                    from app.services.career_service import compute_resume_score, suggest_career_domains
                    stored_entities = analysis.extracted_entities or {}
                    career_score = compute_resume_score(analysis.resume_text, stored_entities)
                    career_domains = suggest_career_domains(stored_entities.get("skills", []))
                except Exception:
                    career_score, career_domains = None, []

                # Update analysis
                analysis.match_score = match_score
                analysis.ats_score = ats_score
                analysis.matched_skills = matched_skills
                analysis.missing_skills = missing_skills
                analysis.feedback = {**feedback, "ats_issues": ats_issues,
                                     "resume_score": career_score, "career_domains": career_domains}
                analysis.skill_roadmap = roadmap

                # Generate PDF
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
                    # Upload PDF to S3
                    report_key = upload_pdf_report(pdf_bytes, str(analysis.id))
                    if report_key:
                        analysis.report_s3_key = report_key
                        report_url = get_presigned_url(report_key, expires_in=86400 * 7)
                        analysis.report_url = report_url

                        # Send email (non-blocking)
                        try:
                            sent = send_analysis_report_email(
                                user.email, user.full_name,
                                report_url or "", match_score, ats_score
                            )
                            analysis.report_emailed = sent
                        except Exception:
                            pass  # Email failure must never break analysis

                analysis.status = AnalysisStatus.completed
                await session.commit()

            except Exception as e:
                analysis.status = AnalysisStatus.failed
                analysis.error_message = str(e)
                await session.commit()
                raise self.retry(exc=e, countdown=60)

        await engine.dispose()

    asyncio.run(_run())

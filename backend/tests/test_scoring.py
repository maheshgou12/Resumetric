import pytest
from app.services.analysis_engine import (
    compute_match_score,
    compute_ats_score,
    detect_skills,
    generate_skill_roadmap,
)
from app.services.career_service import (
    compute_resume_score,
    suggest_career_domains,
)

SAMPLE_RESUME = """
ARJUN MEHTA
arjun.mehta@example.com | +91 98765 43210
Summary: Full-stack software engineer with 3 years experience building Python, FastAPI, React apps.
Skills: Python, FastAPI, React, PostgreSQL, Docker, Git, SQL, REST API
Experience: Software Engineer at Acme Corp. Built API handling 50k requests/day. Reduced latency by 35%.
Education: B.Tech Computer Science, 2023
Projects: Built e-commerce platform using React, FastAPI, Docker.
"""

SAMPLE_JD = """
We are looking for a Software Engineer with experience in Python, FastAPI, React, Docker, and Kubernetes.
The ideal candidate will have strong SQL and REST API knowledge.
"""

def test_compute_match_score():
    score = compute_match_score(SAMPLE_RESUME, SAMPLE_JD)
    assert isinstance(score, float)
    assert score > 0.0
    assert score <= 100.0

def test_compute_ats_score():
    score, issues = compute_ats_score(SAMPLE_RESUME, SAMPLE_JD)
    assert isinstance(score, float)
    assert score > 0.0
    assert score <= 100.0
    assert isinstance(issues, list)

def test_detect_skills():
    matched, missing = detect_skills(SAMPLE_RESUME, SAMPLE_JD)
    assert "Python" in matched
    assert "FastAPI" in matched
    assert "Kubernetes" in missing

def test_generate_skill_roadmap():
    roadmap = generate_skill_roadmap(["Kubernetes", "Docker"])
    assert len(roadmap) == 2
    assert any(item["skill"] == "Kubernetes" for item in roadmap)

def test_compute_resume_score():
    entities = {"skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Git", "SQL", "REST API"]}
    result = compute_resume_score(SAMPLE_RESUME, entities)
    assert "overall" in result
    assert result["overall"] > 0
    assert "grade" in result
    assert "breakdown" in result

def test_suggest_career_domains():
    skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    domains = suggest_career_domains(skills)
    assert len(domains) > 0
    assert any("Backend" in d["domain"] for d in domains)


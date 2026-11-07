"""
CareerLens AI — Career intelligence engine.
Explainable 100-pt resume score, career-domain matching,
skill-gap analysis, roadmaps, interview prep.
Pure-Python, no external API required (Groq optional elsewhere).
"""
import re
from difflib import SequenceMatcher

# ─── 1. Explainable 100-pt Resume Score ─────────────────────────────────────
# Skills 25 | Experience 20 | Projects 20 | Keywords 15 | Education 10 | Completeness 5

SECTION_PATTERNS = {
    "summary": r"\b(summary|objective|profile|about\s*me)\b",
    "experience": r"\b(work\s*experience|professional\s*experience|employment|experience)\b",
    "education": r"\b(education|academic|university|college|degree|b\.?tech|m\.?tech|bachelor|master|ph\.?d)\b",
    "skills": r"\b(skills|technical\s*skills|core\s*competencies|tech\s*stack)\b",
    "projects": r"\b(projects?|personal\s*projects?|academic\s*projects?)\b",
    "certifications": r"\b(certifications?|licenses?|certificate)\b",
    "achievements": r"\b(achievements?|awards?|accomplishments?|honors?)\b",
}

ACTION_VERBS = [
    "built", "developed", "designed", "implemented", "led", "created",
    "optimized", "automated", "deployed", "launched", "improved",
    "managed", "architected", "engineered", "delivered", "increased",
    "reduced", "achieved", "collaborated", "spearheaded",
]

GENERIC_KEYWORDS = [
    "team", "project", "developed", "experience", "worked", "built",
    "managed", "led", "python", "javascript", "sql", "api", "git",
    "agile", "testing", "design", "data", "cloud",
]


def detect_sections(text: str) -> dict:
    low = text.lower()
    return {name: bool(re.search(pat, low)) for name, pat in SECTION_PATTERNS.items()}


def compute_resume_score(resume_text: str, entities: dict) -> dict:
    """Explainable overall score out of 100 with 6 sub-scores."""
    text = resume_text or ""
    low = text.lower()
    words = text.split()
    sections = detect_sections(text)
    skills = entities.get("skills", []) if entities else []
    detail: dict = {}
    strengths, weaknesses, missing = [], [], []

    # — Skills /25: breadth of detected tech skills —
    n_skills = len(skills)
    if n_skills >= 12:
        skills_score = 25
    elif n_skills >= 8:
        skills_score = 20
    elif n_skills >= 5:
        skills_score = 15
    elif n_skills >= 3:
        skills_score = 10
    elif n_skills >= 1:
        skills_score = 6
    else:
        skills_score = 0
    detail["skills"] = {"score": skills_score, "max": 25, "count": n_skills}
    if n_skills >= 8:
        strengths.append(f"Strong skill coverage ({n_skills} technologies detected)")
    else:
        weaknesses.append(f"Only {n_skills} skills detected — add a dedicated Skills section")
        missing.append("Add more relevant technologies to Skills section")

    # — Experience /20: section + action verbs + quantified results + length —
    exp_score = 0
    if sections.get("experience"):
        exp_score += 8
    else:
        weaknesses.append("Missing Work Experience section header")
        missing.append("Add a 'Work Experience' section with role, company, dates, bullets")
    verbs_found = sum(1 for v in ACTION_VERBS if v in low)
    exp_score += min(6, verbs_found * 2)
    quant = len(re.findall(r"\d+\s?[%+]|\$\s?\d+|\b\d+\s?(users|clients|projects?|tests?|ms|s|x\b)", low))
    exp_score += min(6, quant * 2)
    exp_score = min(20, exp_score)
    detail["experience"] = {"score": exp_score, "max": 20,
                            "action_verbs": verbs_found, "quantified": quant}
    if verbs_found >= 3 and quant >= 1:
        strengths.append("Experience uses action verbs and quantified impact")
    else:
        weaknesses.append("Experience bullets lack action verbs / numbers")
        missing.append("Quantify impact (e.g. 'Reduced latency 40%', 'Served 10k users')")

    # — Projects /20 —
    proj_score = 0
    if sections.get("projects"):
        proj_score += 8
    else:
        weaknesses.append("No Projects section detected")
        missing.append("Add 2–3 projects with stack, link, and outcome")
    proj_mentions = len(re.findall(r"\b(project|built|github|deployed|demo)\b", low))
    proj_score += min(6, proj_mentions)
    if entities.get("github"):
        proj_score += 3
    if re.search(r"github\.com|live demo|deployed|http", low):
        proj_score += 3
    proj_score = min(20, proj_score)
    detail["projects"] = {"score": proj_score, "max": 20}
    if proj_score >= 14:
        strengths.append("Projects show hands-on building with links/stack")

    # — Keywords /15: ATS keyword richness —
    kw_hits = sum(1 for k in GENERIC_KEYWORDS if k in low)
    kw_score = min(15, int(kw_hits / len(GENERIC_KEYWORDS) * 15) + (2 if len(words) > 250 else 0))
    kw_score = min(15, kw_score)
    detail["keywords"] = {"score": kw_score, "max": 15, "hits": kw_hits}
    if kw_score < 8:
        weaknesses.append("Low ATS keyword density — mirror job-description terms")
        missing.append("Mirror JD keywords (tools, methods, domain terms)")

    # — Education /10 —
    edu_score = 0
    if sections.get("education"):
        edu_score += 6
    else:
        weaknesses.append("Education section not detected")
        missing.append("Add Education (degree, university, year)")
    if re.search(r"\b(b\.?tech|m\.?tech|bachelor|master|bca|mca|ph\.?d|degree|university|college|cgpa|gpa)\b", low):
        edu_score += 4
    detail["education"] = {"score": edu_score, "max": 10}

    # — Completeness /5: contact + LinkedIn/GitHub + length —
    comp = 0
    if entities.get("emails"):
        comp += 1
    else:
        missing.append("Add email address")
    if entities.get("phones"):
        comp += 1
    else:
        missing.append("Add phone number")
    if entities.get("linkedin"):
        comp += 1
    else:
        missing.append("Add LinkedIn URL")
    if entities.get("github"):
        comp += 1
    else:
        missing.append("Add GitHub URL")
    if 200 <= len(words) <= 1200:
        comp += 1
    elif len(words) < 200:
        weaknesses.append(f"Resume short ({len(words)} words) — aim for 300+ words")
    detail["completeness"] = {"score": comp, "max": 5, "words": len(words)}

    total = (skills_score + exp_score + proj_score + kw_score + edu_score + comp)
    if total >= 85:
        grade, verdict = "A", "Placement-ready. Minor polish only."
    elif total >= 70:
        grade, verdict = "B", "Strong foundation. Fix weak sections below."
    elif total >= 50:
        grade, verdict = "C", "Needs focused improvement before applying."
    else:
        grade, verdict = "D", "Major gaps — follow the roadmap before applying."

    return {
        "overall": total, "max": 100, "grade": grade, "verdict": verdict,
        "breakdown": {
            "skills": {"score": skills_score, "max": 25},
            "experience": {"score": exp_score, "max": 20},
            "projects": {"score": proj_score, "max": 20},
            "keywords": {"score": kw_score, "max": 15},
            "education": {"score": edu_score, "max": 10},
            "completeness": {"score": comp, "max": 5},
        },
        "detail": detail,
        "strengths": strengths[:6],
        "weaknesses": weaknesses[:8],
        "missing_info": missing[:8],
    }


# ─── 2. Career Domain Discovery ─────────────────────────────────────────────

CAREER_DOMAINS = {
    "Frontend Development": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Tailwind", "Vue", "Angular", "Next.js", "Redux"],
    "Backend Development": ["Python", "Java", "Node.js", "FastAPI", "Django", "Flask", "Express", "Spring Boot", "PostgreSQL", "REST API", "Microservices"],
    "Full-Stack Development": ["React", "Node.js", "Python", "PostgreSQL", "REST API", "Git", "Docker"],
    "Data Science / ML": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn", "pandas", "NumPy", "SQL", "Spark"],
    "Data Analytics": ["SQL", "Python", "Power BI", "Tableau", "Data Analysis", "pandas", "Excel"],
    "DevOps / Cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux", "Jenkins", "GitHub Actions"],
    "Mobile Development": ["Kotlin", "Swift", "React", "Flutter", "Firebase"],
    "QA / Test Engineering": ["Selenium", "Testing", "Agile", "Scrum", "Jira", "CI/CD"],
    "UI/UX Design": ["Figma", "Design", "Communication"],
    "Project / Product Management": ["Agile", "Scrum", "Jira", "Project Management", "Leadership", "Communication", "Strategic Planning"],
}


def suggest_career_domains(skills: list[str], top_n: int = 3) -> list[dict]:
    """Rank career domains by skill overlap."""
    have = {s.lower() for s in (skills or [])}
    ranked = []
    for domain, req in CAREER_DOMAINS.items():
        req_low = [r.lower() for r in req]
        matched = [r for r in req if r.lower() in have]
        coverage = len(matched) / len(req) if req else 0
        missing = [r for r in req if r.lower() not in have][:5]
        ranked.append({
            "domain": domain,
            "match_pct": round(coverage * 100, 1),
            "matched": matched[:8],
            "missing": missing,
            "role_examples": _roles_for(domain),
        })
    ranked.sort(key=lambda d: d["match_pct"], reverse=True)
    return ranked[:top_n]


def _roles_for(domain: str) -> list[str]:
    return {
        "Frontend Development": ["Frontend Developer", "React Developer", "UI Engineer"],
        "Backend Development": ["Backend Developer", "API Engineer", "Python Developer"],
        "Full-Stack Development": ["Full-Stack Developer", "Software Engineer"],
        "Data Science / ML": ["ML Engineer", "Data Scientist", "AI Engineer"],
        "Data Analytics": ["Data Analyst", "BI Analyst"],
        "DevOps / Cloud": ["DevOps Engineer", "Cloud Engineer", "SRE"],
        "Mobile Development": ["Android Developer", "iOS Developer", "Flutter Developer"],
        "QA / Test Engineering": ["QA Engineer", "SDET"],
        "UI/UX Design": ["UI/UX Designer", "Product Designer"],
        "Project / Product Management": ["Project Manager", "Scrum Master", "Product Manager"],
    }.get(domain, ["Associate Engineer"])


# ─── 3. Job comparison + skill gap ──────────────────────────────────────────

def compare_with_job(resume_skills: list[str], jd_text: str, all_skills: list[str]) -> dict:
    def _has(text_low: str, skill: str) -> bool:
        s = skill.lower()
        if len(s) <= 3 or skill in ("Java", "R", "Go", "SQL", "PHP"):
            return bool(re.search(r"(?<![a-z0-9+#])" + re.escape(s) + r"(?![a-z0-9+#])", text_low))
        return s in text_low
    jd_low = (jd_text or "").lower()
    resume_low = {s.lower() for s in (resume_skills or [])}
    jd_skills = [s for s in all_skills if _has(jd_low, s)]
    matched = [s for s in jd_skills if s.lower() in resume_low]
    missing = [s for s in jd_skills if s.lower() not in resume_low]
    pct = round(len(matched) / len(jd_skills) * 100, 1) if jd_skills else 0.0
    return {"jd_skills": jd_skills, "matched": matched, "missing": missing,
            "coverage_pct": pct, "total": len(jd_skills)}


# ─── 4. Learning roadmap ────────────────────────────────────────────────────

ROADMAPS = {
    "React": ["JS fundamentals", "Components and props", "Hooks", "Router + API calls", "Build 2 projects"],
    "Python": ["Syntax and OOP", "File/API handling", "FastAPI or Django", "Build REST API project"],
    "SQL": ["SELECT/JOIN", "Aggregations", "Subqueries", "Practice on SQLZoo/LeetCode"],
    "Docker": ["Containers vs VMs", "Dockerfile", "Compose", "Deploy one app"],
    "AWS": ["IAM/EC2/S3 basics", "Deploy static site", "RDS + Lambda", "Free-tier project"],
    "Machine Learning": ["Python + pandas", "scikit-learn basics", "Model evaluation", "Kaggle mini-project"],
}


def roadmap_for_skill(skill: str) -> dict:
    steps = ROADMAPS.get(skill, ["Basics of " + skill, "Guided tutorial", "Mini-project", "Add to resume"])
    resources = {
        "React": "https://react.dev/learn",
        "Python": "https://docs.python.org/3/tutorial/",
        "SQL": "https://sqlzoo.net",
        "Docker": "https://docs.docker.com/get-started/",
        "AWS": "https://aws.amazon.com/training/",
        "Machine Learning": "https://course.fast.ai",
    }
    return {"skill": skill, "steps": steps,
            "resource": resources.get(skill, f"https://www.coursera.org/search?query={skill}"),
            "est_time": "1–4 weeks"}


# ─── 5. Interview prep ──────────────────────────────────────────────────────

def interview_questions(domain: str, skills: list[str]) -> list[dict]:
    bank = {
        "Frontend Development": ["Explain the virtual DOM.", "Controlled vs uncontrolled components?", "How do you optimize React rendering?"],
        "Backend Development": ["Explain REST status codes.", "How do you handle auth (JWT)?", "SQL vs NoSQL trade-offs?"],
        "Data Science / ML": ["Bias vs variance?", "How do you handle imbalanced data?", "Explain overfitting fixes."],
        "DevOps / Cloud": ["What is CI/CD?", "Docker vs VM?", "How do you secure secrets?"],
    }
    qs = bank.get(domain, ["Tell me about yourself.", "Describe a challenging project.", "How do you learn new tech?"])
    skill_q = [f"What is your experience with {s}?" for s in (skills or [])[:2]]
    return [{"question": q, "tip": "Answer with STAR + metric"} for q in (qs + skill_q)][:6]


# ─── 6. Resume version diff ─────────────────────────────────────────────────

def diff_texts(old: str, new: str) -> dict:
    sm = SequenceMatcher(None, old or "", new or "")
    return {
        "similarity_pct": round(sm.ratio() * 100, 1),
        "words_before": len((old or "").split()),
        "words_after": len((new or "").split()),
        "words_added": max(0, len((new or "").split()) - len((old or "").split())),
    }

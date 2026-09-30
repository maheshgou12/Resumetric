"""
AI-powered scoring engine:
- TF-IDF cosine match score
- ATS compatibility scoring
- Missing skills detection
- Groq LLM feedback generation
"""
import re
from typing import Optional
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings


# ─────────────────────────────────────────────────────────────────────────────
# Match Score (TF-IDF Cosine Similarity)
# ─────────────────────────────────────────────────────────────────────────────

def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Returns a 0-100 match score using TF-IDF cosine similarity.
    """
    if not resume_text or not job_description:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 1)
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# ATS Compatibility Score
# ─────────────────────────────────────────────────────────────────────────────

ATS_SECTION_HEADERS = [
    r'\b(work\s*experience|professional\s*experience|experience)\b',
    r'\b(education|academic\s*background)\b',
    r'\b(skills|technical\s*skills|core\s*competencies)\b',
    r'\b(summary|objective|profile|about)\b',
    r'\b(certifications?|licenses?)\b',
    r'\b(projects?)\b',
]

CONTACT_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email
    r'(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3,5}\)?[\s\-]?)?\d{3,5}[\s\-]?\d{4,6}',  # phone (incl. +91 .....)
]


def compute_ats_score(resume_text: str) -> tuple[float, list[str]]:
    """
    Returns (score 0-100, list of issues found)
    Checks:
    - Has contact info (email + phone)
    - Has standard section headers
    - No excessive special characters
    - Reasonable length
    - No images-only content (verified by text existence)
    """
    score = 100.0
    issues = []
    text_lower = resume_text.lower()

    # Check contact info
    has_email = bool(re.search(CONTACT_PATTERNS[0], resume_text))
    has_phone = bool(re.search(CONTACT_PATTERNS[1], resume_text))

    if not has_email:
        score -= 15
        issues.append("No email address detected")
    if not has_phone:
        score -= 10
        issues.append("No phone number detected")

    # Check section headers
    found_sections = 0
    for pattern in ATS_SECTION_HEADERS:
        if re.search(pattern, text_lower):
            found_sections += 1

    if found_sections < 3:
        score -= 20
        issues.append(f"Only {found_sections} of 6 standard section headers detected (Experience, Education, Skills, etc.)")
    elif found_sections < 5:
        score -= 10
        issues.append(f"Only {found_sections} of 6 standard section headers detected")

    # Check text length
    word_count = len(resume_text.split())
    if word_count < 100:
        score -= 20
        issues.append("Resume appears very short (< 100 words)")
    elif word_count < 200:
        score -= 10
        issues.append("Resume is relatively short (< 200 words)")

    # Check for excessive special characters (possible formatting issues)
    special_chars = len(re.findall(r'[|●■□►▶◆★☆✓✔✗✘]', resume_text))
    if special_chars > 30:
        score -= 10
        issues.append(f"High use of special characters ({special_chars}) may confuse ATS parsers")

    # Check if text is coherent (not just a list of special chars)
    if len(resume_text.strip()) < 50:
        score -= 30
        issues.append("Very little text extracted — possible image-only resume or scan")

    return max(0.0, round(score, 1)), issues


# ─────────────────────────────────────────────────────────────────────────────
# Skills Analysis
# ─────────────────────────────────────────────────────────────────────────────

COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL",
    "React", "Vue", "Angular", "Next.js", "Svelte", "HTML", "CSS", "Tailwind",
    "Bootstrap", "jQuery", "Redux", "GraphQL",
    "FastAPI", "Django", "Flask", "Express", "Node.js", "Spring Boot", "Laravel",
    "Rails", "ASP.NET", "NestJS",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
    "DynamoDB", "Cassandra", "Firebase",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD",
    "GitHub Actions", "Jenkins", "Ansible",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn",
    "pandas", "NumPy", "Spark", "Hadoop", "Power BI", "Tableau",
    "REST API", "Microservices", "Agile", "Scrum", "Git", "Linux",
    "Figma", "Jira", "Kafka", "RabbitMQ",
    "Leadership", "Communication", "Problem Solving", "Team Management",
    "Project Management", "Data Analysis", "Strategic Planning",
]


def detect_skills(
    resume_text: str, job_description: str
) -> tuple[list[str], list[str]]:
    """
    Returns (matched_skills, missing_skills)
    Skills present in JD but not in resume = missing
    Skills present in both = matched
    Uses word-boundary matching for short/ambiguous tokens (R, Java, SQL...).
    """
    def _has(text_low: str, skill: str) -> bool:
        s = skill.lower()
        if len(s) <= 3 or skill in ("Java", "R", "Go", "SQL", "PHP"):
            return bool(re.search(r"(?<![a-z0-9+#])" + re.escape(s) + r"(?![a-z0-9+#])", text_low))
        return s in text_low

    jd_lower = job_description.lower()
    resume_lower = resume_text.lower()

    jd_skills = [s for s in COMMON_SKILLS if _has(jd_lower, s)]
    matched = [s for s in jd_skills if _has(resume_lower, s)]
    missing = [s for s in jd_skills if not _has(resume_lower, s)]

    return matched, missing


# ─────────────────────────────────────────────────────────────────────────────
# LLM Feedback (Groq)
# ─────────────────────────────────────────────────────────────────────────────

def generate_llm_feedback(
    resume_text: str,
    job_description: str,
    match_score: float,
    ats_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
) -> dict:
    """
    Call Groq LLM to generate structured qualitative feedback.
    Returns dict with: strengths, weaknesses, suggestions, rewrite_tips, cover_letter_hint
    """
    if not settings.GROQ_API_KEY:
        return _fallback_feedback(match_score, ats_score, missing_skills)

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""You are an expert career coach and resume analyst. Analyze the following resume against a job description and provide structured, actionable feedback.

MATCH SCORE: {match_score}%
ATS SCORE: {ats_score}%
MATCHED SKILLS: {', '.join(matched_skills[:15]) if matched_skills else 'None detected'}
MISSING SKILLS: {', '.join(missing_skills[:15]) if missing_skills else 'None detected'}

JOB DESCRIPTION (first 1000 chars):
{job_description[:1000]}

RESUME TEXT (first 1500 chars):
{resume_text[:1500]}

Respond ONLY with valid JSON in this exact format:
{{
  "overall_summary": "2-3 sentence executive summary of the resume-JD match",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "suggestions": [
    {{"section": "Summary", "suggestion": "specific actionable rewrite tip"}},
    {{"section": "Experience", "suggestion": "specific actionable rewrite tip"}},
    {{"section": "Skills", "suggestion": "specific actionable rewrite tip"}}
  ],
  "rewrite_tips": ["specific bullet point rewrite 1", "specific bullet point rewrite 2"],
  "interview_tips": ["tip 1", "tip 2"],
  "priority_action": "The single most impactful change to make right now"
}}"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
        )
        content = response.choices[0].message.content
        # Extract JSON from response
        import json
        # Find JSON block
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        return _fallback_feedback(match_score, ats_score, missing_skills)
    except Exception as e:
        print(f"LLM error: {e}")
        return _fallback_feedback(match_score, ats_score, missing_skills)


def _fallback_feedback(
    match_score: float, ats_score: float, missing_skills: list[str]
) -> dict:
    """Fallback when Groq is unavailable"""
    return {
        "overall_summary": f"Your resume achieved a {match_score}% match score and {ats_score}% ATS compatibility. There is room for improvement.",
        "strengths": ["Resume has been submitted for analysis"],
        "weaknesses": [f"Missing {len(missing_skills)} key skills from the job description"],
        "suggestions": [
            {"section": "Skills", "suggestion": f"Add these missing skills if you have them: {', '.join(missing_skills[:5])}"}
        ],
        "rewrite_tips": ["Quantify your achievements with numbers and percentages"],
        "interview_tips": ["Research the company thoroughly before the interview"],
        "priority_action": f"Add the missing skills ({', '.join(missing_skills[:3])}) to your resume if applicable",
    }


def generate_skill_roadmap(missing_skills: list[str]) -> list[dict]:
    """
    For each missing skill, suggest a learning resource.
    Uses Groq if available, otherwise returns curated defaults.
    """
    RESOURCE_MAP = {
        "Python": {"resource": "Python.org Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "time": "2-4 weeks"},
        "JavaScript": {"resource": "javascript.info", "url": "https://javascript.info", "time": "3-6 weeks"},
        "React": {"resource": "React Official Docs", "url": "https://react.dev/learn", "time": "2-4 weeks"},
        "Docker": {"resource": "Docker Getting Started", "url": "https://docs.docker.com/get-started/", "time": "1-2 weeks"},
        "AWS": {"resource": "AWS Free Training", "url": "https://aws.amazon.com/training/", "time": "4-8 weeks"},
        "Machine Learning": {"resource": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai", "time": "8-12 weeks"},
        "SQL": {"resource": "SQLZoo Interactive Tutorial", "url": "https://sqlzoo.net", "time": "1-2 weeks"},
        "Kubernetes": {"resource": "Kubernetes.io Tutorial", "url": "https://kubernetes.io/docs/tutorials/", "time": "3-5 weeks"},
        "TypeScript": {"resource": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/", "time": "1-2 weeks"},
        "Git": {"resource": "Git Official Book (free)", "url": "https://git-scm.com/book", "time": "1 week"},
    }

    roadmap = []
    for skill in missing_skills[:8]:  # Limit to 8 skills
        if skill in RESOURCE_MAP:
            roadmap.append({
                "skill": skill,
                **RESOURCE_MAP[skill],
                "priority": "high" if skill in missing_skills[:3] else "medium",
            })
        else:
            roadmap.append({
                "skill": skill,
                "resource": f"Search for '{skill}' on Coursera or YouTube",
                "url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
                "time": "Varies",
                "priority": "medium",
            })
    return roadmap

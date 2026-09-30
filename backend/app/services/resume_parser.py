"""
Resume text extraction from PDF and DOCX files
"""
import io
from typing import Optional
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import docx


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF bytes using pdfminer"""
    output = io.StringIO()
    with io.BytesIO(file_content) as pdf_file:
        extract_text_to_fp(
            pdf_file,
            output,
            laparams=LAParams(),
            output_type="text",
            codec="utf-8",
        )
    text = output.getvalue()
    return text.strip()


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX bytes"""
    with io.BytesIO(file_content) as docx_file:
        doc = docx.Document(docx_file)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text)
    return "\n".join(paragraphs)


def extract_text(file_content: bytes, content_type: str, filename: str) -> str:
    """Auto-detect and extract text from PDF or DOCX"""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_content)
    elif content_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ) or filename.lower().endswith((".docx", ".doc")):
        return extract_text_from_docx(file_content)
    raise ValueError(f"Unsupported file type: {content_type}")


def extract_entities(resume_text: str) -> dict:
    """
    CareerLens AI — full structured extraction:
    name, email, phone, linkedin, github, education, skills,
    technologies, experience, projects, certifications, achievements, sections.
    """
    import re

    entities = {
        "emails": [],
        "phones": [],
        "skills": [],
        "technologies": [],
        "name": None,
        "linkedin": None,
        "github": None,
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "sections": {},
    }

    # Email / phone
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, resume_text)
    phone_pattern = r'(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3,5}\)?[\s\-]?)?\d{3,5}[\s\-]?\d{4,6}'
    candidates = re.findall(phone_pattern, resume_text)
    phones = []
    for c in candidates:
        digits = re.sub(r"\D", "", c)
        if 10 <= len(digits) <= 13 and len(c.strip()) >= 10:
            phones.append(c.strip())
    # Filter out year-like numbers (e.g. 2023-2024)
    phones = [p for p in phones if not re.fullmatch(r"20\d{2}\s*-\s*20\d{2}", p)]
    entities["phones"] = phones

    # LinkedIn / GitHub
    li = re.search(r"(linkedin\.com/in/[\w\-/]+)", resume_text, re.IGNORECASE)
    if li:
        entities["linkedin"] = "https://" + li.group(1)
    gh = re.search(r"(github\.com/[\w\-/]+)", resume_text, re.IGNORECASE)
    if gh:
        entities["github"] = "https://" + gh.group(1).rstrip("/.,)")

    # Common tech skills detection
    SKILL_KEYWORDS = [
        # Languages
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL",
        # Frontend
        "React", "Vue", "Angular", "Next.js", "Svelte", "HTML", "CSS", "Tailwind",
        "Bootstrap", "jQuery", "Redux", "GraphQL",
        # Backend
        "FastAPI", "Django", "Flask", "Express", "Node.js", "Spring Boot", "Laravel",
        "Rails", "ASP.NET", "NestJS",
        # Database
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
        "DynamoDB", "Cassandra", "Firebase",
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD",
        "GitHub Actions", "Jenkins", "Ansible",
        # Data & AI
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn",
        "pandas", "NumPy", "Spark", "Hadoop", "Power BI", "Tableau",
        # Other
        "REST API", "Microservices", "Agile", "Scrum", "Git", "Linux",
        "Figma", "Jira", "Kafka", "RabbitMQ", "Selenium", "Flutter",
    ]
    text_lower = resume_text.lower()
    found_skills = []
    for skill in SKILL_KEYWORDS:
        s = skill.lower()
        # Short / ambiguous tokens need word-boundary match
        if len(s) <= 3 or skill in ("Java", "R", "Go", "C", "C++", "C#", "SQL", "PHP"):
            if re.search(r"(?<![a-z0-9+#])" + re.escape(s) + r"(?![a-z0-9+#])", text_lower):
                found_skills.append(skill)
        else:
            if s in text_lower:
                found_skills.append(skill)
    entities["skills"] = found_skills
    entities["technologies"] = found_skills  # alias for CareerLens spec

    # Section detection
    pats = {
        "summary": r"\b(summary|objective|profile|about\s*me)\b",
        "experience": r"\b(work\s*experience|professional\s*experience|employment|experience)\b",
        "education": r"\b(education|academic)\b",
        "skills": r"\b(skills|technical\s*skills|core\s*competencies)\b",
        "projects": r"\b(projects?)\b",
        "certifications": r"\b(certifications?|licenses?|certificate)\b",
        "achievements": r"\b(achievements?|awards?|accomplishments?|honors?)\b",
    }
    entities["sections"] = {k: bool(re.search(p, text_lower)) for k, p in pats.items()}

    # Section-sliced extraction (grab up to ~6 lines after each header)
    lines = [l.strip() for l in resume_text.split("\n")]
    non_empty = [l for l in lines if l.strip()]

    def _slice(keywords: list[str], max_lines: int = 8) -> list[str]:
        out: list[str] = []
        for i, l in enumerate(non_empty):
            if any(k in l.lower() for k in keywords):
                for nxt in non_empty[i + 1: i + 1 + max_lines]:
                    if any(h in nxt.lower() for h in
                           ["experience", "education", "skills", "projects", "certification", "achievement", "summary"]):
                        break
                    if len(nxt) > 2:
                        out.append(nxt)
                break
        return out[:max_lines]

    entities["education"] = _slice(["education", "academic", "university", "b.tech", "bachelor"]) or \
        [l for l in non_empty if re.search(r"\b(b\.?tech|m\.?tech|bachelor|master|university|college|cgpa|\d{4})\b", l, re.I)][:4]
    entities["experience"] = _slice(["work experience", "professional experience", "employment", "experience"]) or \
        [l for l in non_empty if re.search(r"\b(intern|engineer|developer|analyst|manager|20\d{2})\b", l, re.I)][:6]
    entities["projects"] = _slice(["project", "personal project"]) or \
        [l for l in non_empty if re.search(r"\b(built|developed|github|deployed|project)\b", l, re.I)][:6]
    entities["certifications"] = _slice(["certification", "certificate", "licensed"]) or \
        [l for l in non_empty if re.search(r"\b(certified|aws certified|azure|google cloud|certificate)\b", l, re.I)][:4]
    entities["achievements"] = _slice(["achievement", "award", "accomplishment", "honor"]) or \
        [l for l in non_empty if re.search(r"\b(award|rank|won|hackathon|competition|first|top \d+)\b", l, re.I)][:4]

    # Try to extract name from first lines
    if non_empty:
        # Heuristic: first non-empty line is often the name
        first_line = non_empty[0]
        if len(first_line.split()) <= 5 and first_line[0].isupper():
            entities["name"] = first_line

    return entities

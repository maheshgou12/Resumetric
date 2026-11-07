"""
CareerLens AI — Database Seeding Script.
Populates sample users (admin + demo user) and sample resume analysis data
so the dashboard and charts are immediately populated.

Usage:
    cd backend
    python seed_demo.py
"""
import sqlite3
import uuid
import json
from datetime import datetime, timedelta, timezone
from app.core.security import get_password_hash

DB_PATH = "careerlens.db"

DEMO_RESUME_TEXT = """
ARJUN MEHTA
arjun.mehta@example.com | +91 98765 43210 | linkedin.com/in/arjunmehta | github.com/arjunmehta

SUMMARY
Full-Stack Software Engineer with 3+ years of experience building scalable web applications using React, Python, FastAPI, and PostgreSQL. Passionate about clean code, high performance, and cloud-native architecture.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS
Frameworks & Libraries: React, FastAPI, Node.js, Express, Tailwind CSS, Redux
Databases: PostgreSQL, MySQL, Redis, SQLite
Tools & Cloud: Docker, Git, GitHub Actions, AWS, REST API, Linux, CI/CD

PROFESSIONAL EXPERIENCE
Software Engineer | Acme Tech Solutions (2023 - Present)
- Architected and deployed microservices using FastAPI and PostgreSQL, serving 100k+ active users.
- Reduced API response latency by 42% through query optimization and Redis caching layers.
- Led front-end migration to React with TypeScript, improving page load speed by 35%.
- Implemented CI/CD pipelines with GitHub Actions and Docker, reducing deployment cycle times by 50%.

Associate Software Engineer | CodeCraft Studio (2021 - 2023)
- Built interactive dashboard features in React and Tailwind CSS for enterprise analytics clients.
- Developed RESTful APIs in Python with automated unit and integration test coverage exceeding 90%.
- Collaborated in an Agile Scrum team with bi-weekly sprints, code reviews, and product demos.

EDUCATION
Bachelor of Technology in Computer Science & Engineering
XYZ University, 2021 | GPA: 3.8 / 4.0

PROJECTS
CareerLens AI — Resume Intelligence Platform (React, FastAPI, Docker)
- Built an AI-powered resume parser and scoring engine computing match scores and ATS compatibility.
- Deployed on AWS with automated CI/CD and secure token-based authentication.

CloudShop E-Commerce API (FastAPI, PostgreSQL, Redis)
- High-concurrency checkout and payment processing engine handling 5,000 requests/minute.
"""

SAMPLE_JD = """
Senior Full-Stack Engineer — Cloud Platform
We are looking for a skilled Full-Stack Engineer with strong expertise in Python, FastAPI, React, TypeScript, Docker, Kubernetes, and AWS.
Responsibilities include building robust backend microservices, optimizing database performance in PostgreSQL and Redis, and deploying scalable distributed systems.
Requirements:
- 3+ years experience with Python (FastAPI or Django) and React.
- Strong knowledge of PostgreSQL, Redis, REST APIs, Git, and Docker.
- Experience with Kubernetes, AWS, and CI/CD pipelines is a strong plus.
"""

def seed():
    print(f"🌱 Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")

    # Create tables if not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id CHAR(36) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        hashed_password VARCHAR(255),
        role VARCHAR(10) DEFAULT 'user' NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_verified BOOLEAN DEFAULT 0,
        google_id VARCHAR(255) UNIQUE,
        avatar_url VARCHAR(500),
        analyses_this_month INTEGER DEFAULT 0,
        analyses_month_reset TIMESTAMP,
        dark_mode BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id CHAR(36) PRIMARY KEY,
        user_id CHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        version INTEGER DEFAULT 1 NOT NULL,
        target_role VARCHAR(255),
        filename VARCHAR(500),
        content TEXT,
        entities JSON,
        resume_score JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id CHAR(36) PRIMARY KEY,
        user_id CHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        resume_filename VARCHAR(500),
        resume_s3_key VARCHAR(500),
        resume_text TEXT,
        job_description TEXT NOT NULL,
        job_title VARCHAR(255),
        company_name VARCHAR(255),
        status VARCHAR(20) DEFAULT 'pending' NOT NULL,
        match_score FLOAT,
        ats_score FLOAT,
        matched_skills JSON,
        missing_skills JSON,
        extracted_entities JSON,
        feedback JSON,
        skill_roadmap JSON,
        report_s3_key VARCHAR(500),
        report_url VARCHAR(1000),
        report_emailed BOOLEAN DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id CHAR(36) PRIMARY KEY,
        user_id CHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash VARCHAR(255) UNIQUE NOT NULL,
        is_revoked BOOLEAN DEFAULT 0,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_verifications (
        id CHAR(36) PRIMARY KEY,
        user_id CHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token VARCHAR(255) UNIQUE NOT NULL,
        is_used BOOLEAN DEFAULT 0,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id CHAR(36) PRIMARY KEY,
        user_id CHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token VARCHAR(255) UNIQUE NOT NULL,
        is_used BOOLEAN DEFAULT 0,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # Check if demo users already exist
    cursor.execute("SELECT id FROM users WHERE email = 'admin@careerlens.ai'")
    if cursor.fetchone():
        print("⚠️ Database already seeded! Existing demo accounts:")
        print("   Admin: admin@careerlens.ai / Admin@12345")
        print("   User:  demo@careerlens.ai  / Demo@12345")
        conn.close()
        return

    print("👤 Creating demo users...")
    admin_id = str(uuid.uuid4())
    demo_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO users (id, email, full_name, hashed_password, role, is_active, is_verified, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (admin_id, "admin@careerlens.ai", "Admin User", get_password_hash("Admin@12345"), "admin", 1, 1, now_str, now_str))

    cursor.execute("""
    INSERT INTO users (id, email, full_name, hashed_password, role, is_active, is_verified, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (demo_id, "demo@careerlens.ai", "Arjun Mehta", get_password_hash("Demo@12345"), "user", 1, 1, now_str, now_str))

    print("📄 Creating sample resume...")
    entities = {
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "Git", "Redis", "REST API", "SQL", "Linux", "CI/CD"],
        "emails": ["arjun.mehta@example.com"],
        "phones": ["+91 98765 43210"],
        "github": "https://github.com/arjunmehta",
        "linkedin": "https://linkedin.com/in/arjunmehta",
    }
    resume_score = {
        "overall": 82,
        "grade": "A",
        "verdict": "Strong, well-structured resume with great technical breadth.",
        "breakdown": {
            "skills": {"score": 25, "max": 25},
            "experience": {"score": 18, "max": 20},
            "projects": {"score": 18, "max": 20},
            "keywords": {"score": 11, "max": 15},
            "education": {"score": 10, "max": 10},
        },
        "strengths": ["Strong skill coverage (12+ technologies)", "Experience features action verbs & metrics"],
        "weaknesses": ["Add Kubernetes certification or experience to reach 90+"],
    }
    resume_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO resumes (id, user_id, name, version, target_role, filename, content, entities, resume_score, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (resume_id, demo_id, "FullStack-Resume", 1, "Senior Full-Stack Engineer", "Arjun_Mehta_Resume_v1.pdf", DEMO_RESUME_TEXT, json.dumps(entities), json.dumps(resume_score), now_str, now_str))

    print("📊 Creating sample analysis history...")
    analyses_data = [
        (
            str(uuid.uuid4()), demo_id, "Arjun_Mehta_Resume.pdf", DEMO_RESUME_TEXT, SAMPLE_JD,
            "Senior Full-Stack Engineer", "CloudScale Technologies", "completed", 88.5, 85.0,
            json.dumps(["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Redis", "Docker", "Git", "REST API"]),
            json.dumps(["Kubernetes", "AWS"]),
            json.dumps(entities),
            json.dumps({
                "overall_summary": "Exceptional fit for Senior Full-Stack role. Strong backend engineering and React experience.",
                "strengths": ["Matched 9 out of 11 critical job skills", "Quantified accomplishments in work experience"],
                "weaknesses": ["Missing Kubernetes orchestration experience mentioned in job posting"],
                "suggestions": [
                    {"section": "Skills", "suggestion": "Highlight container orchestration if you have any hands-on Kubernetes or Helm experience."}
                ],
                "priority_action": "Add Kubernetes to skills section and mention containerized deployments.",
            }),
            json.dumps([
                {"skill": "Kubernetes", "resource": "Kubernetes.io Official Tutorial", "time": "3-5 weeks", "priority": "high", "url": "https://kubernetes.io/docs/tutorials/"},
                {"skill": "AWS", "resource": "AWS Skill Builder & Cloud Practitioner", "time": "4-8 weeks", "priority": "medium", "url": "https://aws.amazon.com/training/"},
            ]),
            (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            str(uuid.uuid4()), demo_id, "Arjun_Mehta_Resume.pdf", DEMO_RESUME_TEXT,
            "Backend Python Engineer requiring Python, Django, PostgreSQL, Celery, and Docker.",
            "Backend Python Developer", "DataFlow Systems", "completed", 82.0, 88.0,
            json.dumps(["Python", "PostgreSQL", "Docker", "Git", "SQL"]),
            json.dumps(["Django", "Celery"]),
            json.dumps(entities),
            json.dumps({"overall_summary": "Strong backend foundation.", "strengths": ["Great database and Python experience"]}),
            json.dumps([]),
            (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            str(uuid.uuid4()), demo_id, "Arjun_Mehta_Resume.pdf", DEMO_RESUME_TEXT,
            "React Frontend Developer requiring React, TypeScript, Redux, and Tailwind CSS.",
            "React Frontend Developer", "PixelCraft UI", "completed", 78.5, 80.0,
            json.dumps(["React", "TypeScript", "Redux", "Tailwind CSS"]),
            json.dumps(["Next.js"]),
            json.dumps(entities),
            json.dumps({"overall_summary": "Solid frontend skill alignment.", "strengths": ["Strong React and styling expertise"]}),
            json.dumps([]),
            (datetime.now(timezone.utc) - timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S")
        ),
    ]

    for a in analyses_data:
        cursor.execute("""
        INSERT INTO analyses (id, user_id, resume_filename, resume_text, job_description, job_title, company_name, status, match_score, ats_score, matched_skills, missing_skills, extracted_entities, feedback, skill_roadmap, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*a, a[-1]))

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("🎉 Database successfully seeded with demo data!")
    print("=" * 60)
    print("Login credentials:")
    print("  🔑 Admin Account:")
    print("     Email:    admin@careerlens.ai")
    print("     Password: Admin@12345")
    print("     Access:   Full User Features + Admin Dashboard (/admin)")
    print("")
    print("  🔑 Demo User Account:")
    print("     Email:    demo@careerlens.ai")
    print("     Password: Demo@12345")
    print("     Access:   Pre-loaded resumes, scores, and analysis trends")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    seed()

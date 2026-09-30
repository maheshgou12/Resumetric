# ⚡ Resume Analyzer Pro

> AI-powered resume analysis platform — match score, ATS compatibility, missing skills, personalized coaching, PDF reports, and more.

[![CI/CD](https://github.com/yourusername/resume-analyzer-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/resume-analyzer-pro/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🚀 Live Demo

| Service | URL |
|---------|-----|
| Frontend | `https://resume-analyzer-pro.vercel.app` |
| Backend API | `https://resume-analyzer-api.onrender.com` |
| API Docs | `https://resume-analyzer-api.onrender.com/docs` |
| Health Check | `https://resume-analyzer-api.onrender.com/health` |

---

## ✨ Features

### Core
- **AI Match Score** — TF-IDF cosine similarity between resume and job description (0–100%)
- **ATS Compatibility Score** — Checks section headers, contact info, formatting issues
- **Skills Gap Analysis** — Detects 60+ skills, shows matched vs. missing
- **LLM Feedback** — Groq (llama-3.3-70b) generates strengths, weaknesses, rewrite tips
- **PDF Report** — Professional ReportLab PDF with all scores and recommendations
- **Email Delivery** — Resend API delivers report to user's inbox automatically

### Authentication
- Email + password with strength enforcement
- Email verification (account soft-verified on signup, banner until confirmed)
- Google OAuth via Google Identity Services (verified server-side)
- JWT access tokens (30 min) + httpOnly cookie refresh tokens (7 days)
- Refresh token rotation with server-side revocation
- Forgot/reset password with 15-minute single-use tokens

### Dashboards
- **User Dashboard** — Analysis history table, match/ATS trend line chart
- **Admin Dashboard** — Platform stats, top missing skills bar chart, signup trend, searchable analysis/user tables

### Advanced
- **AI Rewrite Coach** — Chat panel backed by Groq LLM with resume + JD context
- **Cover Letter Generator** — One-click tailored cover letter
- **Skill Roadmap** — Curated free resources for each missing skill
- **Rate Limiting** — 5 free analyses/month per user, enforced server-side

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite, Tailwind CSS v4, React Router v7, Recharts, Axios |
| Backend | FastAPI (Python 3.11), SQLAlchemy 2.0 async, Pydantic v2 |
| Database | PostgreSQL (Neon/Render) |
| File Storage | Cloudflare R2 / AWS S3 (boto3) |
| Auth | JWT + httpOnly cookie, passlib/bcrypt, Google Identity Services |
| Email | Resend API |
| AI | Groq API (llama-3.3-70b), scikit-learn TF-IDF |
| PDF | ReportLab |
| Background | Celery + Redis |
| Hosting | Vercel (frontend) + Render (backend) |
| CI/CD | GitHub Actions |
| Monitoring | Sentry + UptimeRobot |

---

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker + Docker Compose (for PostgreSQL + Redis)

### 1. Clone & configure

```bash
git clone https://github.com/yourusername/resume-analyzer-pro.git
cd resume-analyzer-pro

# Backend config
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend config
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local
```

### 2. Start services (DB + Redis)

```bash
docker compose up postgres redis -d
```

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Start Celery worker (optional, for async analysis)

```bash
cd backend
celery -A app.celery_tasks worker --loglevel=info -Q analysis,email
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
# App running at http://localhost:5173
```

---

## 🔑 Required Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `JWT_SECRET_KEY` | Random 256-bit string | ✅ |
| `SECRET_KEY` | App secret key | ✅ |
| `GROQ_API_KEY` | [groq.com](https://console.groq.com) API key | ✅ |
| `RESEND_API_KEY` | [resend.com](https://resend.com) API key | ✅ |
| `S3_ACCESS_KEY_ID` | Cloudflare R2 or AWS S3 | ✅ |
| `S3_SECRET_ACCESS_KEY` | S3 secret | ✅ |
| `S3_BUCKET_NAME` | S3/R2 bucket name | ✅ |
| `S3_ENDPOINT_URL` | R2 endpoint URL (omit for AWS) | R2 only |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | For Google Login |
| `REDIS_URL` | Redis connection URL | For Celery |
| `SENTRY_DSN` | Sentry project DSN | Optional |
| `FRONTEND_URL` | Frontend URL for email links | ✅ |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (use `/api/v1` with Vite proxy) |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |

---

## 🚀 Deployment

### Frontend → Vercel

1. Import GitHub repo in [vercel.com](https://vercel.com)
2. Set root directory to `frontend`
3. Add env vars: `VITE_API_URL=https://your-api.onrender.com/api/v1`, `VITE_GOOGLE_CLIENT_ID`
4. Deploy — Vercel handles SPA routing via `vercel.json`

### Backend → Render

1. Connect GitHub repo in [render.com](https://render.com)
2. Create a **Web Service** pointing to `backend/`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables in the Render dashboard
6. Set up a **PostgreSQL** database on Render/Neon and link the connection string

### Auto-deploy (CI/CD)

Add these secrets to your GitHub repo:
- `RENDER_DEPLOY_HOOK_URL` — from Render's deploy hooks
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` — from Vercel

### Monitoring

- Add `/health` endpoint URL to [UptimeRobot](https://uptimerobot.com) with 10-min interval to prevent cold starts
- Add `SENTRY_DSN` to backend environment for error tracking

---

## 📁 Project Structure

```
resume-analyzer/
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
├── docker-compose.yml          # Local dev services
├── frontend/
│   ├── src/
│   │   ├── components/         # Navbar, GoogleButton, ProtectedRoute
│   │   ├── context/            # AuthContext (auth state)
│   │   ├── lib/                # Axios client with token refresh
│   │   └── pages/              # All page components
│   ├── vercel.json             # Vercel SPA config
│   └── vite.config.js          # Vite + Tailwind config
└── backend/
    ├── app/
    │   ├── api/v1/             # FastAPI routes (auth, analysis, users, admin)
    │   ├── core/               # Config, database, security, deps
    │   ├── models/             # SQLAlchemy models
    │   └── services/           # AI engine, PDF, email, S3, resume parser
    ├── main.py                 # FastAPI app entry point
    ├── Dockerfile              # Backend container
    └── requirements.txt        # Python dependencies
```

---

## 🔒 Security Notes

- Refresh tokens stored as SHA-256 hashes (never raw)
- httpOnly cookies prevent XSS token theft
- Password reset tokens expire in 15 minutes and are single-use
- Anti-enumeration on forgot-password (always returns 200)
- File uploads validated by MIME type + extension + size (5MB max)
- Rate limiting: 5 analyses/month on free tier
- CORS locked to known origins

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

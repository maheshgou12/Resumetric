# ⚡ CareerLens AI — Resumetric

> AI-powered resume & career intelligence: JD-aware match + ATS scores, skills gaps, rewrite coaching, cover letters, roadmaps, interview prep, PDF reports — unlimited analyses for every account.

**Primary Production URL:** https://resumetric-1.onrender.com (Unified React 19 Frontend + FastAPI Backend)  
**Edge CDN Frontend:** https://resumetric-challengers13.vercel.app  
**API Documentation:** https://resumetric-1.onrender.com/docs · **Health Check:** https://resumetric-1.onrender.com/health

---

## ✨ Features

### Analysis (unlimited per account)
- **AI Match Score** — TF-IDF cosine similarity between resume and job description
- **JD-aware ATS Score** — format (40) + JD skill coverage (35) + JD keyword overlap (25), with point-wise reasons
- **Skills Gap** — 75+ detected skills, matched vs missing, learning roadmap with free resources
- **LLM Feedback** — Groq (`llama-3.3-70b-versatile` with automatic model fallback & offline heuristics)
- **AI Rewrite Coach** — chat with resume + JD context, structured markdown replies
- **Cover Letter Generator** — one-click tailored letter
- **PDF Report** — ReportLab report with scores, skills, roadmap
- **100-pt Resume Score + Career Domains** — offline heuristic, 10 domains ranked by fit
- **Interview Prep** — domain questions + STAR tips · **Progress trends** · **Resume library** (versions, compare, re-analyze)

### Accounts & Mail
- Email + password (bcrypt, strength rules, case-insensitive) and Google OAuth (server-verified)
- Secure signup with explicit login (email pre-filled upon account creation)
- JWT access (30 min) + rotating cross-origin httpOnly refresh cookies (`SameSite=None` in production)
- Email verification & forgot/reset password via **Gmail SMTP** (SSL/STARTTLS) → Brevo HTTPS → Resend fallback
- Email verification & forgot/reset password delivered directly to user inbox with secure single-use tokens
- User dashboard (history, stats, trends) + admin dashboard (platform stats, missing skills, user search)

---

## 🛠️ Run Locally

### 1-Click Launch (Windows)
Double-click `start-dev.bat` or run:
```powershell
.\start-dev.ps1
```
This automatically starts:
- **Backend API**: http://127.0.0.1:8000 (Swagger docs at `/docs`)
- **Frontend App**: http://localhost:5173

---

### Manual Launch (Two Terminals)

Prerequisites: Python 3.11+, Node.js 20+.

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

---

## 🔑 Pre-Seeded Demo Accounts

To explore the dashboard and analytics immediately without manual entry, run:
```bash
cd backend
python seed_demo.py
```

| Account | Email | Password | Access Level |
|---|---|---|---|
| **Admin** | `admin@careerlens.ai` | `Admin@12345` | Full features + Admin Analytics Dashboard (`/admin`) |
| **Demo User** | `demo@careerlens.ai` | `Demo@12345` | Pre-loaded resumes, ATS 85%, Match 88.5%, and charts |

---

## ✉️ Email Testing (Gmail SMTP)

To test your Gmail SMTP connection and verify emails land in your inbox:
```bash
cd backend
python test_email.py
```

---

## 🏗️ Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 19 + Vite, Tailwind v4, Router v7, React Query, Recharts, Axios, react-markdown |
| Backend | FastAPI, SQLAlchemy 2 async (SQLite WAL / PostgreSQL asyncpg), Pydantic v2, bcrypt/JWT, Groq, scikit-learn, ReportLab |
| Email | Gmail SMTP (465/587) → Brevo HTTPS → Resend fallback |
| Deploy | Vercel (Edge CDN Frontend) + Render (Backend + Managed PostgreSQL) |

---

## 🚀 Deploy to Production (Anytime, Globally)

### 1. Push to GitHub
```bash
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

### 2. Backend → Render
1. Go to [dashboard.render.com](https://dashboard.render.com) -> **New +** -> **Blueprint**.
2. Select your repository (Render automatically reads `render.yaml`).
3. Set your environment variables in the Render dashboard:
   - `JWT_SECRET_KEY`: Random 32+ character key
   - `SECRET_KEY`: Random 32+ character key
   - `FRONTEND_URL`: Your Vercel frontend URL
   - `ALLOWED_ORIGINS`: Your Vercel frontend URL
   - `SMTP_USERNAME` & `SMTP_APP_PASSWORD`: Your Gmail & App Password
4. Deploy! Render provisions the FastAPI Web Service + PostgreSQL database with free SSL.

### 3. Frontend → Vercel
1. In [Vercel](https://vercel.com), click **Add New** -> **Project** -> Import your repo.
2. Root Directory: `frontend`
3. Environment Variables:
   - `VITE_API_URL`: `https://<your-render-backend-url>/api/v1`
4. Deploy! Your app is instantly distributed across Vercel's global edge network.

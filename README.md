# ⚡ CareerLens AI — Resumetric

> AI-powered resume & career intelligence: JD-aware match + ATS scores, skills gaps, rewrite coaching, cover letters, roadmaps, interview prep, PDF reports — unlimited analyses for every account.

**Live app:** https://resumetric-challengers13.vercel.app
**API:** https://resumetric-rus3.onrender.com · **Docs:** https://resumetric-rus3.onrender.com/docs · **Health:** https://resumetric-rus3.onrender.com/health

---

## ✨ Features

### Analysis (unlimited per account)
- **AI Match Score** — TF-IDF cosine similarity between resume and job description
- **JD-aware ATS Score** — format (40) + JD skill coverage (35) + JD keyword overlap (25), with point-wise reasons
- **Skills Gap** — 75+ detected skills, matched vs missing, learning roadmap with free resources
- **LLM Feedback** — Groq (`openai/gpt-oss-120b`): verdict, strengths, weaknesses, priority action
- **AI Rewrite Coach** — chat with resume + JD context, structured markdown replies
- **Cover Letter Generator** — one-click tailored letter
- **PDF Report** — ReportLab report with scores, skills, roadmap
- **100-pt Resume Score + Career Domains** — offline heuristic, 10 domains ranked by fit
- **Interview Prep** — domain questions + STAR tips · **Progress trends** · **Resume library** (versions, compare, re-analyze)

### Accounts & mail (per-user, any inbox)
- Email + password (bcrypt, strength rules, case-insensitive) and Google OAuth (server-verified)
- JWT access (30 min) + rotating httpOnly refresh cookies (7 days)
- Email verification, forgot/reset password (15-min single-use tokens, anti-enumeration, 60s throttle)
- Mail via Brevo HTTPS API (any inbox) → Gmail SMTP → Resend fallback
- User dashboard (history, stats, trends) + admin dashboard (platform stats, missing skills, user search)

---

## 🛠️ Run locally

Prerequisites: Python 3.11+, Node.js 20+.

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill GROQ_API_KEY + mail keys (see below)
python -m uvicorn main:app --reload   # http://127.0.0.1:8000, docs at /docs

# Frontend (second terminal)
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

Local defaults need zero setup: SQLite database auto-creates, analysis runs inline (no Redis needed).

### Minimal `.env` for full local features

| Key | Get it at | Enables |
|---|---|---|
| `GROQ_API_KEY` | console.groq.com | AI feedback, chat, cover letters |
| `BREVO_API_KEY` + `BREVO_SENDER_EMAIL` | brevo.com (verify sender, no domain needed) | Real mail to any inbox |
| `GOOGLE_CLIENT_ID` (+ secret) | Google Cloud Console | Continue-with-Google (`http://localhost:5173` in JS origins) |
| `SMTP_USERNAME` + `SMTP_APP_PASSWORD` | myaccount.google.com/apppasswords | Local mail fallback |

Without mail keys, reset/verify links print to the backend console (dev mode).

---

## 🏗️ Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 19 + Vite, Tailwind v4, Router v7, React Query, Recharts, Axios, react-markdown |
| Backend | FastAPI, SQLAlchemy 2 async, Pydantic v2, bcrypt/JWT, Groq, scikit-learn, ReportLab |
| Data | SQLite (local) / PostgreSQL (prod, asyncpg) |
| Mail | Brevo HTTPS → Gmail SMTP → Resend |
| Deploy | Vercel (frontend) + Render + Render Postgres (backend) |

## 📁 Structure

```
├── render.yaml            # Render blueprint (backend + database)
├── vercel.json            # SPA rewrites + security headers
├── docker-compose.yml     # Local Postgres + Redis (optional)
├── backend/
│   ├── main.py            # App entry, CORS, /health
│   ├── app/api/v1/        # auth, analysis, career, users, admin
│   ├── app/core/          # config (env-driven), database, security, guards
│   ├── app/models/        # User, Analysis, Resume, tokens
│   └── app/services/      # scoring engine, parser, PDF, mail, storage
└── frontend/src/
    ├── pages/             # 16 pages (landing → dashboards → legal)
    ├── components/        # Navbar, GoogleButton, ProtectedRoute
    ├── context/           # Auth state + token refresh
    └── lib/api.js         # Axios client
```

## 🚀 Deploy (how this repo is live)

- **Frontend → Vercel:** import repo, root `frontend/` (repo-root `vercel.json` also works with build `cd frontend && npm run build`, output `frontend/dist`). Env: `VITE_API_URL=https://<api>/api/v1`, `VITE_GOOGLE_CLIENT_ID`.
- **Backend → Render:** Blueprint/new web service, `rootDir backend`, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`. Attach Postgres; env: `JWT_SECRET_KEY`, `SECRET_KEY`, `GROQ_API_KEY`, mail keys, `GOOGLE_*`, `FRONTEND_URL` + `ALLOWED_ORIGINS` (= Vercel URL).
- **Google OAuth for all users:** add the Vercel URL to Authorized JavaScript origins, fill Branding URLs (`/privacy`, `/terms` exist), Publish the app.

## 🔒 Security notes

- Refresh tokens stored as SHA-256 hashes; httpOnly cookies; single-use short-lived reset tokens
- Case-insensitive email identity; Google-only accounts get guidance mail instead of silent failure
- Uploads validated (type + 5MB); naive-UTC datetimes for Postgres compatibility; secrets never committed (see `.gitignore`)

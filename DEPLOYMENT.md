# 🌐 CareerLens AI — 24/7 Global Production Deployment Guide

This guide details how to deploy **CareerLens AI** globally online for **free, forever, with 24/7 uptime, zero sleeping (no cold starts), and unlimited analyses**.

---

## Architecture Options

| Option | Frontend | Backend | Database | Sleep Behavior | Setup Time |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A (Recommended)** | Bundled with Backend | Render Web Service | PostgreSQL / SQLite | **Zero sleep** (via 10-min keep-alive ping) | 3 mins |
| **Option B (Split)** | Vercel (Edge CDN) | Render Web Service | PostgreSQL / SQLite | **Zero sleep** (via 10-min keep-alive ping) | 5 mins |
| **Option C (Alternative)** | Bundled with Backend | Koyeb | PostgreSQL / SQLite | **Zero sleep** (always awake by design) | 3 mins |
| **Option D (HuggingFace)** | Bundled with Backend | HF Spaces (Docker) | SQLite | **Zero sleep** (16GB RAM, 24/7 free) | 2 mins |
| **Option E (VPS/Docker)** | React/Nginx container | FastAPI container | PostgreSQL + Redis | **Self-hosted 24/7** | 1 command |

---

## Option A: One-Click Unified Deployment on Render (24/7 Zero-Sleep)

Because CareerLens AI compiles the React 19 frontend into `frontend/dist` and FastAPI serves it directly via SPA fallback, you can deploy the **entire application with one URL**.

### Step 1: Deploy on Render
1. Go to [dashboard.render.com](https://dashboard.render.com/) and click **New → Web Service**.
2. Connect your GitHub repository: `maheshgou12/Resumetric`.
3. Configure the service:
   - **Name:** `careerlens-ai`
   - **Environment:** `Docker` (or `Python 3`)
   - **Region:** Any (e.g. `Oregon (US West)` or `Frankfurt (EU)`)
   - **Branch:** `main`
   - **Plan:** `Free`
4. In the **Environment Variables** section, add:
   ```env
   APP_ENV=production
   DEBUG=False
   SECRET_KEY=generate-any-random-32-char-string
   JWT_SECRET_KEY=generate-any-random-32-char-string
   GROQ_API_KEY=<YOUR_GROQ_API_KEY>
   GROQ_MODEL=qwen/qwen3.8-27b
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USERNAME=<YOUR_GMAIL_ADDRESS>
   SMTP_APP_PASSWORD=<YOUR_GMAIL_16_CHAR_APP_PASSWORD>
   EMAIL_FROM_NAME=CareerLens AI
   ```
5. Click **Create Web Service**. Render will automatically build the container and provide your live URL (e.g., `https://careerlens-ai.onrender.com`).

---

### Step 2: Prevent Render From Sleeping (Keep-Alive Automation)

Render's free tier automatically pauses services after 15 minutes of zero traffic. By setting up a free external ping every 10 minutes, **your service stays awake 24/7/365 with ZERO cold starts**:

1. Go to [UptimeRobot.com](https://uptimerobot.com/) (100% Free).
2. Click **Add New Monitor**.
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `CareerLens Keep-Alive`
   - **URL (or IP):** `https://resumetric-1.onrender.com/health` (or your custom domain)
   - **Monitoring Interval:** `Every 10 minutes` (or `Every 5 minutes`)
3. Click **Create Monitor**.

🎉 **Result:** UptimeRobot pings `/health` every 10 minutes. Render never goes to sleep, your users never experience spin-down delays, and the platform remains responsive worldwide 24 hours a day!

---

## Option B: Split Deployment (Vercel Frontend + Render Backend)

If you prefer deploying the frontend onto Vercel's global Edge CDN:

### 1. Deploy Frontend on Vercel
1. Go to [vercel.com/new](https://vercel.com/new) and import `maheshgou12/Resumetric`.
2. Configure project settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Add Environment Variable:
   - `VITE_API_URL` = `https://your-backend-name.onrender.com/api/v1`
4. Click **Deploy**. Vercel will assign a URL like `https://resumetric.vercel.app`.

### 2. Update Backend CORS
In Render's Environment settings for your backend, set:
```env
ALLOWED_ORIGINS=https://resumetric.vercel.app,http://localhost:5173
```
*(The backend also automatically allows any `*.vercel.app` domain via regex).*

---

## Option C: Koyeb Deployment (Free Tier Does Not Sleep)

Koyeb offers free nano compute instances that **do not spin down or sleep**:

1. Go to [app.koyeb.com](https://app.koyeb.com/) and click **Create App**.
2. Select **GitHub** and pick `maheshgou12/Resumetric`.
3. Choose **Dockerfile** (uses the root `Dockerfile`).
4. Set Port to `8000`.
5. Enter your environment variables (`GROQ_API_KEY`, `SMTP_USERNAME`, `SMTP_APP_PASSWORD`, etc.).
6. Click **Deploy**. Koyeb will launch your app with a global `*.koyeb.app` URL that runs 24/7 continuously.

---

## Option D: Hugging Face Spaces (Free 16GB RAM, Always On)

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) → **Create new Space**.
2. Choose **Docker** as the SDK and select **Blank**.
3. Push your repository to the Hugging Face Space git remote.
4. Add your secrets in **Settings → Variables and Secrets**.
5. The space runs a 16GB RAM container 24/7 with a persistent public URL.

---

## Option E: Full Self-Hosted Docker Compose (VPS / Server)

To run the entire architecture on any VPS (DigitalOcean, AWS EC2, Linode, Hetzner, etc.):

```bash
# Clone the repository
git clone https://github.com/maheshgou12/Resumetric.git
cd Resumetric

# Launch the entire production stack (PostgreSQL + Redis + FastAPI + Celery + React)
docker-compose up -d --build
```

Access:
- **Web Platform:** `http://your-server-ip:3000`
- **FastAPI Documentation:** `http://your-server-ip:8000/docs`
- **Celery Flower Monitor:** `http://your-server-ip:5555`

---

## Default Admin Credentials
Every fresh deployment automatically seeds a default administrator account:
- **Email:** `admin@careerlens.ai`
- **Password:** `Admin@12345`
*(Remember to change the admin password under `/settings` once deployed).*

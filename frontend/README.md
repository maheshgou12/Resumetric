# 🎨 CareerLens AI — Frontend

> Modern, high-performance career intelligence dashboard built with React 19, Vite 8, and Tailwind CSS v4.

---

## ⚡ Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **React 19** | Component-driven UI with modern hooks and transitions |
| **Vite 8** | Lightning-fast HMR and optimized production bundling |
| **Tailwind CSS v4** | Modern dark-mode-first aesthetic with fluid gradients |
| **React Router v7** | Declarative client-side routing with protected route guards |
| **TanStack React Query** | Asynchronous state management and caching |
| **Recharts** | Data visualization for match scores, ATS radar, and progress trends |
| **Axios** | HTTP client with automatic JWT token refresh interceptors |
| **React Hook Form + Zod** | Schema-driven form validation with accessible error messaging |

---

## 📁 Directory Structure

```text
frontend/src/
├── assets/          # Static brand images and logos
├── components/      # Reusable UI widgets (Navbar, GoogleButton, ProtectedRoute)
├── context/         # AuthContext and global application state
├── lib/             # Axios API client, interceptors, and constants
├── pages/           # Application views
│   ├── LandingPage.jsx         # Marketing & overview page
│   ├── LoginPage.jsx           # Explicit email/password login
│   ├── RegisterPage.jsx        # Account creation & password strength meter
│   ├── PasswordPages.jsx       # Forgot password & reset password views
│   ├── DashboardPage.jsx       # User dashboard, recent analyses, & trends
│   ├── AnalyzePage.jsx         # Upload resume & job description analyzer
│   ├── AnalysisResultsPage.jsx # Deep-dive score breakdown & gap analysis
│   ├── ResumesPage.jsx         # Resume library & version history
│   ├── RoadmapPage.jsx         # Step-by-step career skill roadmap
│   ├── InterviewPage.jsx       # AI interview prep questions & STAR tips
│   ├── SettingsPage.jsx        # Profile management & appearance settings
│   └── AdminDashboardPage.jsx  # Platform metrics & administrator controls
├── App.jsx          # Route definitions & layout wrappers
└── main.jsx         # Application entry point & QueryClient provider
```

---

## 🛠️ Development

```bash
# Install dependencies
npm install

# Start development server with HMR
npm run dev

# Compile optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

---

## 🌐 Production Deployment

The frontend can be deployed in two modes:
1. **Unified (Recommended):** Compiled into `dist/` and served directly by the FastAPI backend on [Render](https://resumetric-1.onrender.com).
2. **Edge CDN:** Deployed as an independent static application on [Vercel](https://resumetric-challengers13.vercel.app) with proxy rewrites to the FastAPI API.

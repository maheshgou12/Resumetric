import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'

// Code-split: each page loads on demand so the first paint stays light.
// (Landing + auth shell stay in the main bundle for instant load.)
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const PasswordPages = lazy(() => import('./pages/PasswordPages').then(m => ({ default: m.ForgotPasswordPage })))
const ResetPasswordPage = lazy(() => import('./pages/PasswordPages').then(m => ({ default: m.ResetPasswordPage })))
const VerifyEmailPage = lazy(() => import('./pages/VerifyEmailPage'))
const AnalyzePage = lazy(() => import('./pages/AnalyzePage'))
const CareerLensPage = lazy(() => import('./pages/CareerLensPage'))
const ResumesPage = lazy(() => import('./pages/ResumesPage'))
const ProgressPage = lazy(() => import('./pages/ProgressPage'))
const RoadmapPage = lazy(() => import('./pages/RoadmapPage'))
const InterviewPage = lazy(() => import('./pages/InterviewPage'))
const AnalysisResultsPage = lazy(() => import('./pages/AnalysisResultsPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'))
const LegalPages = lazy(() => import('./pages/LegalPages').then(m => ({ default: m.TermsPage })))
const PrivacyPage = lazy(() => import('./pages/LegalPages').then(m => ({ default: m.PrivacyPage })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
})

function Layout({ children, hideNav = false }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {!hideNav && <Navbar />}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {children}
      </main>
    </div>
  )
}

function PageFallback() {
  return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '4rem 1rem' }}>
      <div style={{ textAlign: 'center' }}>
        <div className="animate-spin" style={{
          width: 40, height: 40, borderRadius: '50%',
          border: '3px solid rgba(99,102,241,0.2)',
          borderTop: '3px solid #6366f1', margin: '0 auto 1rem',
        }} />
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>Loading page...</p>
      </div>
    </div>
  )
}

function LazyPage({ children, hideNav = false }) {
  return (
    <Layout hideNav={hideNav}>
      <Suspense fallback={<PageFallback />}>
        {children}
      </Suspense>
    </Layout>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Layout><LandingPage /></Layout>} />
            <Route path="/login" element={<LazyPage hideNav><LoginPage /></LazyPage>} />
            <Route path="/register" element={<LazyPage hideNav><RegisterPage /></LazyPage>} />
            <Route path="/forgot-password" element={<LazyPage hideNav><PasswordPages /></LazyPage>} />
            <Route path="/reset-password" element={<LazyPage hideNav><ResetPasswordPage /></LazyPage>} />
            <Route path="/verify-email" element={<LazyPage hideNav><VerifyEmailPage /></LazyPage>} />
            <Route path="/terms" element={<LazyPage><LegalPages /></LazyPage>} />
            <Route path="/privacy" element={<LazyPage><PrivacyPage /></LazyPage>} />

            {/* Protected routes */}
            <Route path="/analyze" element={
              <ProtectedRoute>
                <LazyPage><AnalyzePage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/analysis/:id" element={
              <ProtectedRoute>
                <LazyPage><AnalysisResultsPage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/career" element={
              <ProtectedRoute>
                <LazyPage><CareerLensPage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/resumes" element={
              <ProtectedRoute>
                <LazyPage><ResumesPage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/progress" element={
              <ProtectedRoute>
                <LazyPage><ProgressPage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/roadmaps" element={
              <ProtectedRoute>
                <LazyPage><RoadmapPage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/interview" element={
              <ProtectedRoute>
                <LazyPage><InterviewPage /></LazyPage>
              </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <LazyPage><DashboardPage /></LazyPage>
              </ProtectedRoute>
            } />

            {/* Admin routes */}
            <Route path="/admin" element={
              <ProtectedRoute adminOnly>
                <LazyPage><AdminDashboardPage /></LazyPage>
              </ProtectedRoute>
            } />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>

          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#e2e8f0',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '0.75rem',
                fontSize: '0.875rem',
                fontFamily: 'Inter, sans-serif',
              },
              success: {
                iconTheme: { primary: '#10b981', secondary: '#1e293b' },
              },
              error: {
                iconTheme: { primary: '#ef4444', secondary: '#1e293b' },
              },
            }}
          />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

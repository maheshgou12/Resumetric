import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  {
    icon: '🔍',
    title: '100-pt Resume Score',
    desc: 'Explainable score out of 100 across Skills, Experience, Projects, Keywords, Education and Completeness — know exactly what to fix.',
    color: '#6366f1',
  },
  {
    icon: '🎯',
    title: 'AI Match Scoring',
    desc: 'TF-IDF cosine similarity + LLM analysis gives you an accurate % match between your resume and any job description.',
    color: '#06b6d4',
  },
  {
    icon: '🤖',
    title: 'ATS Compatibility',
    desc: 'Know if your resume will pass Applicant Tracking Systems before applying. Get specific formatting fixes.',
    color: '#10b981',
  },
  {
    icon: '🧭',
    title: 'Career Domains',
    desc: 'Discover the roles you fit best — Full-Stack, Backend, Data, DevOps — ranked by your actual skills with missing-skill lists.',
    color: '#f59e0b',
  },
  {
    icon: '💡',
    title: 'Skills Gap Analysis',
    desc: 'See exactly which skills the JD requires that your resume is missing — and get a learning roadmap to close the gap.',
    color: '#ec4899',
  },
  {
    icon: '✍️',
    title: 'AI Rewrite Coach',
    desc: 'Chat with an AI career coach that knows your resume and the job. Get specific bullet point rewrites, not generic advice.',
    color: '#8b5cf6',
  },
  {
    icon: '🗺️',
    title: 'Learning Roadmaps',
    desc: 'Step-by-step plans with free resources and time estimates for every missing technology.',
    color: '#14b8a6',
  },
  {
    icon: '🎤',
    title: 'Interview Prep',
    desc: 'Domain-specific interview questions generated from your target role, with STAR answering tips.',
    color: '#f43f5e',
  },
  {
    icon: '📁',
    title: 'Resume Library',
    desc: 'Keep every version of your resume in one place. Re-analyze, compare versions side-by-side, and watch scores climb.',
    color: '#a855f7',
  },
]

const STEPS = [
  { step: '01', title: 'Upload Your Resume', desc: 'Drag & drop your PDF or DOCX resume. We extract and analyze the full content instantly.' },
  { step: '02', title: 'Paste Job Description', desc: 'Copy the job posting you\'re targeting. Our AI reads it to understand exactly what they want.' },
  { step: '03', title: 'Get Your Analysis', desc: 'Receive match scores, ATS report, missing skills, AI feedback, and a downloadable PDF report.' },
]

const STATS = [
  { value: '< 30s', label: 'Analysis Time' },
  { value: '75+', label: 'Skills Detected' },
  { value: '100-pt', label: 'Explainable Score' },
  { value: 'Private', label: 'Your Data Stays Yours' },
]

export default function LandingPage() {
  const { user } = useAuth()

  return (
    <div style={{ flex: 1 }}>
      {/* ─── Hero ─────────────────────────────────────────────────────────── */}
      <section style={{
        position: 'relative', overflow: 'hidden',
        padding: '6rem 1.5rem 5rem', textAlign: 'center',
      }}>
        {/* Background glow */}
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 800, height: 800, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ maxWidth: 780, margin: '0 auto', position: 'relative' }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
            borderRadius: '9999px', padding: '0.375rem 1rem',
            fontSize: '0.8125rem', fontWeight: 600, color: '#a5b4fc',
            marginBottom: '2rem',
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366f1', animation: 'pulse-glow 2s infinite', display: 'inline-block' }} />
            AI-Powered Career Intelligence Platform
          </div>

          <h1 style={{
            fontSize: 'clamp(2.5rem, 6vw, 4rem)',
            fontWeight: 900, lineHeight: 1.1,
            marginBottom: '1.5rem',
            fontFamily: 'var(--font-display)',
          }}>
            Land Your Dream Job with{' '}
            <span className="gradient-text">AI-Powered</span>{' '}
            Resume Analysis
          </h1>

          <p style={{
            fontSize: '1.1875rem', color: '#94a3b8', lineHeight: 1.7,
            marginBottom: '2.5rem', maxWidth: 600, margin: '0 auto 2.5rem',
          }}>
            Upload your resume, paste any job description, and get an instant match score,
            ATS compatibility report, missing-skills breakdown, and personalized AI coaching
            — all in under 30 seconds.
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link
              to={user ? '/analyze' : '/register'}
              className="btn-primary"
              style={{ padding: '0.875rem 2rem', fontSize: '1rem' }}
            >
              ⚡ {user ? 'Analyze My Resume' : 'Get Started Free'}
            </Link>
            <Link to="/login" className="btn-ghost" style={{ padding: '0.875rem 2rem', fontSize: '1rem' }}>
              {user ? '📊 View Dashboard' : 'Log In'}
            </Link>
          </div>

          {/* Stats row */}
          <div style={{
            display: 'flex', justifyContent: 'center', gap: '2.5rem',
            marginTop: '4rem', flexWrap: 'wrap',
          }}>
            {STATS.map(stat => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '1.75rem', fontWeight: 800,
                  fontFamily: 'var(--font-display)',
                  background: 'var(--gradient-brand)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>{stat.value}</div>
                <div style={{ fontSize: '0.8125rem', color: '#64748b', marginTop: 2 }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ─────────────────────────────────────────────────── */}
      <section style={{ padding: '5rem 1.5rem', background: 'rgba(255,255,255,0.02)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>How It Works</h2>
            <p style={{ color: '#64748b', fontSize: '1.0625rem' }}>From upload to insights in 3 simple steps</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            {STEPS.map((step, i) => (
              <div key={i} className="card animate-fade-in-up" style={{
                animationDelay: `${i * 0.1}s`, position: 'relative', overflow: 'hidden',
              }}>
                <div style={{
                  fontSize: '3rem', fontWeight: 900, color: 'rgba(99,102,241,0.08)',
                  fontFamily: 'var(--font-display)', position: 'absolute', top: 8, right: 16,
                  lineHeight: 1,
                }}>{step.step}</div>
                <div style={{
                  width: 40, height: 40, borderRadius: '0.625rem',
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.125rem', fontWeight: 700, color: 'white',
                  marginBottom: '1rem',
                }}>{step.step}</div>
                <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem', fontFamily: 'var(--font-display)' }}>{step.title}</h3>
                <p style={{ color: '#64748b', fontSize: '0.9rem', lineHeight: 1.6 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Features ─────────────────────────────────────────────────────── */}
      <section style={{ padding: '5rem 1.5rem' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ fontSize: '2.25rem', marginBottom: '0.75rem' }}>Everything You Need to Get Hired</h2>
            <p style={{ color: '#64748b', fontSize: '1.0625rem' }}>No guesswork. No generic advice. Just data-driven insights.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {FEATURES.map((feat, i) => (
              <div key={i} className="card card-hover" style={{ animationDelay: `${i * 0.05}s` }}>
                <div style={{
                  width: 48, height: 48, borderRadius: '0.75rem',
                  background: `${feat.color}20`, border: `1px solid ${feat.color}30`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.5rem', marginBottom: '1rem',
                }}>{feat.icon}</div>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem' }}>{feat.title}</h3>
                <p style={{ color: '#64748b', fontSize: '0.875rem', lineHeight: 1.6 }}>{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ──────────────────────────────────────────────────────────── */}
      <section style={{ padding: '5rem 1.5rem' }}>
        <div style={{ maxWidth: 700, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))',
            border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: '1.5rem', padding: '3.5rem 2rem',
          }}>
            <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
              Ready to Optimize Your Resume?
            </h2>
            <p style={{ color: '#94a3b8', marginBottom: '2rem', fontSize: '1.0625rem' }}>
              Join thousands of job seekers getting AI-powered career coaching.
              Start free — no credit card required.
            </p>
            <Link to={user ? '/analyze' : '/register'} className="btn-primary" style={{ fontSize: '1.0625rem', padding: '0.9375rem 2.25rem' }}>
              ⚡ {user ? 'Analyze Another Resume' : 'Start Analyzing for Free'}
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '2rem 1.5rem', textAlign: 'center',
        color: '#475569', fontSize: '0.8125rem',
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <span style={{ fontWeight: 700, color: '#94a3b8' }}>CareerLens AI</span>
          {' '}— placement-ready resume & career intelligence. Built with ⚡ FastAPI + React.
        </div>
      </footer>
    </div>
  )
}

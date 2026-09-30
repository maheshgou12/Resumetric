import { Link } from 'react-router-dom'

const wrap = { maxWidth: 800, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }
const p = { color: '#94a3b8', fontSize: '0.9375rem', lineHeight: 1.7, marginBottom: '1rem' }
const h2 = { fontSize: '1.125rem', margin: '1.75rem 0 0.5rem' }

export function TermsPage() {
  return (
    <div style={wrap}>
      <h1 style={{ fontSize: '2rem', marginBottom: '.5rem' }}>Terms of Service</h1>
      <p style={p}>Last updated: September 2026 · CareerLens AI</p>
      <h2 style={h2}>1. What we provide</h2>
      <p style={p}>CareerLens AI analyzes resumes you upload against job descriptions you paste. Scores (match, ATS, 100-pt) are heuristic + AI-assisted estimates to guide improvement — not hiring guarantees.</p>
      <h2 style={h2}>2. Your content</h2>
      <p style={p}>You keep ownership of resumes you upload. You grant us permission to process them to provide analysis, PDF reports, and history. Do not upload resumes that are not yours or contain sensitive data you are not allowed to share.</p>
      <h2 style={h2}>3. Fair use</h2>
      <p style={p}>Free accounts are limited to 5 analyses per month. Automated scraping, bulk uploads, or API abuse may lead to suspension.</p>
      <h2 style={h2}>4. Accounts</h2>
      <p style={p}>You are responsible for keeping your password confidential and for activity under your account. Verify your email to use all features.</p>
      <h2 style={h2}>5. Liability</h2>
      <p style={p}>The service is provided "as is" without warranties. We are not liable for job-application outcomes based on scores or suggestions.</p>
      <div style={{ marginTop: '2rem' }}><Link to="/register" className="btn-ghost">← Back to sign up</Link></div>
    </div>
  )
}

export function PrivacyPage() {
  return (
    <div style={wrap}>
      <h1 style={{ fontSize: '2rem', marginBottom: '.5rem' }}>Privacy Policy</h1>
      <p style={p}>Last updated: September 2026 · CareerLens AI</p>
      <h2 style={h2}>1. Data we collect</h2>
      <p style={p}>Account data (name, email, password hash), resumes and job descriptions you submit, analysis results, and basic usage logs.</p>
      <h2 style={h2}>2. How we use it</h2>
      <p style={p}>To create your account, run analyses, generate PDF reports, send transactional emails (verification, password reset, report delivery), and show your dashboard history.</p>
      <h2 style={h2}>3. AI processing</h2>
      <p style={p}>Resume and job-description text is sent to our AI provider (Groq) solely to generate feedback, chat answers, and cover letters. We do not sell your data.</p>
      <h2 style={h2}>4. Storage & retention</h2>
      <p style={p}>Data is stored in our database and object storage. You can delete resumes anytime from the Resume Library. Contact support to request full account deletion.</p>
      <h2 style={h2}>5. Your rights</h2>
      <p style={p}>You may access, correct, export, or delete your personal data at any time via the app or by contacting support.</p>
      <div style={{ marginTop: '2rem' }}><Link to="/register" className="btn-ghost">← Back to sign up</Link></div>
    </div>
  )
}

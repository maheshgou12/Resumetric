import { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'

export default function CareerLensPage() {
  const [resumeText, setResumeText] = useState('')
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [compare, setCompare] = useState(null)

  const runScore = async () => {
    if (resumeText.trim().length < 50) return toast.error('Paste resume text (50+ chars)')
    setLoading(true)
    try {
      const r = await api.post('/career/score', { resume_text: resumeText })
      setResult(r.data)
      toast.success(`Score: ${r.data.score.overall}/100 (${r.data.score.grade})`)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Scoring failed')
    } finally { setLoading(false) }
  }

  const runCompare = async () => {
    if (resumeText.trim().length < 50 || jd.trim().length < 20) return toast.error('Need resume + JD')
    setLoading(true)
    try {
      const r = await api.post('/career/job-compare', { resume_text: resumeText, job_description: jd })
      setCompare(r.data)
      toast.success(`JD Match: ${r.data.match_score}% | Missing: ${r.data.missing.length} skills`)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Compare failed')
    } finally { setLoading(false) }
  }

  const bar = (v, max) => ({
    height: 8, borderRadius: 99, background: 'rgba(255,255,255,0.08)', overflow: 'hidden', marginTop: 4,
  })

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '.5rem' }}>CareerLens AI — Resume & Career Analyzer</h1>
      <p style={{ color: '#64748b' }}>Register → Upload → Score (100-pt) → Domains → Job compare → Roadmap → Interview → Re-upload → Track.</p>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h3>Paste resume text (or upload via Analyze page for PDF/DOCX)</h3>
        <textarea className="input" style={{ minHeight: 160 }} value={resumeText} onChange={e => setResumeText(e.target.value)} placeholder="Paste extracted resume text here..." />
        <div style={{ display: 'flex', gap: '.75rem', marginTop: '.75rem', flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={runScore} disabled={loading}>{loading ? 'Scoring...' : 'Get 100-pt Score + Domains'}</button>
          <button className="btn-ghost" onClick={() => setResumeText('ARJUN MEHTA\narjun.mehta@gmail.com | +91 98765 43210 | linkedin.com/in/arjunmehta | github.com/arjunmehta\nSUMMARY: Full-stack developer with 2 years building React and FastAPI apps.\nSKILLS: Python, JavaScript, React, FastAPI, PostgreSQL, Docker, Git, SQL, REST API\nWORK EXPERIENCE: Software Engineer Intern, TechCorp (2023-2024). Built dashboard serving 10k users, reduced latency 40 percent. Developed REST API with FastAPI and PostgreSQL. Led migration to Docker, automated CI/CD.\nEDUCATION: B.Tech Computer Science, Mumbai University, 2024, CGPA 8.5\nPROJECTS: E-commerce app (React, FastAPI) deployed on AWS, github.com/arjunmehta/shop. ML sentiment classifier with scikit-learn, pandas.\nCERTIFICATIONS: AWS Certified Cloud Practitioner\nACHIEVEMENTS: Won Smart India Hackathon 2023')}>Fill sample resume</button>
        </div>
      </div>

      {result && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h2>Overall Score {result.score.overall}/100 — Grade {result.score.grade}</h2>
          <p style={{ color: '#94a3b8' }}>{result.score.verdict}</p>
          {Object.entries(result.score.breakdown).map(([k, v]) => (
            <div key={k} style={{ margin: '.5rem 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.875rem' }}>
                <span style={{ textTransform: 'capitalize' }}>{k}</span><span>{v.score}/{v.max}</span>
              </div>
              <div style={bar()}><div style={{ width: `${(v.score / v.max) * 100}%`, height: '100%', background: 'linear-gradient(90deg,#6366f1,#8b5cf6)' }} /></div>
            </div>
          ))}
          <h3 style={{ marginTop: '1rem' }}>Suitable career domains</h3>
          {result.career_domains.map(d => (
            <div key={d.domain} style={{ padding: '.5rem 0', borderBottom: '1px solid rgba(255,255,255,.06)', fontSize: '.875rem' }}>
              <b>{d.domain}</b> — {d.match_pct}% | Roles: {d.role_examples.join(', ')}<br />
              <span style={{ color: '#34d399' }}>Have: {d.matched.join(', ') || '—'}</span><br />
              <span style={{ color: '#fbbf24' }}>Learn: {d.missing.join(', ')}</span>
            </div>
          ))}
          <h3 style={{ marginTop: '1rem' }}>Strengths / Gaps</h3>
          <ul style={{ fontSize: '.875rem', color: '#cbd5e1' }}>
            {result.score.strengths.map((s, i) => <li key={i}>+ {s}</li>)}
            {result.score.weaknesses.map((s, i) => <li key={i}>! {s}</li>)}
          </ul>
        </div>
      )}

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3>Compare with a job + skill gaps + roadmap</h3>
        <textarea className="input" style={{ minHeight: 120 }} value={jd} onChange={e => setJd(e.target.value)} placeholder="Paste job description..." />
        <div style={{ marginTop: '.75rem' }}><button className="btn-primary" onClick={runCompare} disabled={loading}>Compare & Find Gaps</button></div>
      </div>

      {compare && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h3>Match {compare.match_score}% | ATS {compare.ats_score}% | Coverage {compare.gap.coverage_pct}%</h3>
          <p style={{ fontSize: '.875rem' }}><span style={{ color: '#34d399' }}>Matched: {compare.matched.join(', ') || '—'}</span></p>
          <p style={{ fontSize: '.875rem' }}><span style={{ color: '#f87171' }}>Missing: {compare.missing.join(', ') || 'None'}</span></p>
          <h4>Learn missing tech</h4>
          {compare.roadmap.map(r => (
            <div key={r.skill} style={{ fontSize: '.875rem', padding: '.4rem 0' }}>
              <b>{r.skill}</b> ({r.est_time}): {r.steps.join(' > ')} — <a href={r.resource} target="_blank" rel="noreferrer">{r.resource}</a>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

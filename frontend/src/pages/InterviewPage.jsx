import { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'

const DOMAINS = ['Frontend Development', 'Backend Development', 'Full-Stack Development', 'Data Science / ML', 'Data Analytics', 'DevOps / Cloud', 'Mobile Development', 'QA / Test Engineering', 'UI/UX Design', 'Project / Product Management']

export default function InterviewPage() {
  const [domain, setDomain] = useState('Backend Development')
  const [skills, setSkills] = useState('Python, FastAPI')
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState({})

  const fetchQuestions = async () => {
    setLoading(true)
    try {
      const r = await api.post('/career/interview-prep', { domain, skills })
      setQuestions(r.data.questions)
      setOpen({})
      toast.success(`${r.data.questions.length} questions ready`)
    } catch { toast.error('Interview prep failed — is the backend running?') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      <h1 style={{ fontSize: '1.875rem' }}>Interview Prep</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Domain-specific questions generated from your target role + skills.</p>

      <div className="card">
        <label style={{ fontSize: '.8rem', color: '#94a3b8' }}>Target domain</label>
        <select className="input" value={domain} onChange={e => setDomain(e.target.value)} style={{ marginTop: '.25rem' }}>
          {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <label style={{ fontSize: '.8rem', color: '#94a3b8', marginTop: '.75rem', display: 'block' }}>Your skills (comma-separated)</label>
        <input className="input" value={skills} onChange={e => setSkills(e.target.value)} style={{ marginTop: '.25rem' }} />
        <div style={{ marginTop: '.75rem' }}>
          <button className="btn-primary" disabled={loading} onClick={fetchQuestions}>{loading ? 'Generating...' : 'Generate Questions'}</button>
        </div>
      </div>

      {questions.map((q, i) => (
        <div key={i} className="card" style={{ marginTop: '.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'center' }}>
            <b>Q{i + 1}. {q.question}</b>
            <button className="btn-ghost" onClick={() => setOpen(o => ({ ...o, [i]: !o[i] }))}>{open[i] ? 'Hide tip' : 'Show tip'}</button>
          </div>
          {open[i] && <p style={{ color: '#94a3b8', fontSize: '.875rem', marginTop: '.5rem' }}>Tip: {q.tip} — answer with STAR (Situation, Task, Action, Result) + a metric.</p>}
        </div>
      ))}
    </div>
  )
}

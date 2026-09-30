import { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'

const POPULAR = ['React', 'Python', 'SQL', 'Docker', 'AWS', 'Kubernetes', 'Machine Learning', 'TypeScript', 'Node.js', 'FastAPI']

export default function RoadmapPage() {
  const [skill, setSkill] = useState('')
  const [roadmap, setRoadmap] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchRoadmap = async (s) => {
    const target = (s || skill).trim()
    if (!target) return toast.error('Enter a skill')
    setLoading(true)
    try {
      const r = await api.get(`/career/roadmap/${encodeURIComponent(target)}`)
      setRoadmap(r.data)
    } catch { toast.error('Roadmap failed') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      <h1 style={{ fontSize: '1.875rem' }}>Skill Roadmaps</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Learn missing technologies step-by-step with free resources.</p>

      <div className="card">
        <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap' }}>
          <input className="input" placeholder="e.g. Kubernetes" value={skill} onChange={e => setSkill(e.target.value)} style={{ flex: 1, minWidth: 200 }} />
          <button className="btn-primary" disabled={loading} onClick={() => fetchRoadmap()}>{loading ? '...' : 'Get Roadmap'}</button>
        </div>
        <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap', marginTop: '.75rem' }}>
          {POPULAR.map(p => (
            <button key={p} className="tag tag-purple" style={{ cursor: 'pointer', border: 'none' }} onClick={() => { setSkill(p); fetchRoadmap(p) }}>{p}</button>
          ))}
        </div>
      </div>

      {roadmap && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h2>{roadmap.skill} <span style={{ fontSize: '.8rem', color: '#64748b' }}>({roadmap.est_time})</span></h2>
          <ol style={{ paddingLeft: '1.25rem', color: '#cbd5e1' }}>
            {roadmap.steps.map((s, i) => <li key={i} style={{ margin: '.4rem 0' }}>{s}</li>)}
          </ol>
          <a href={roadmap.resource} target="_blank" rel="noreferrer" style={{ color: '#a5b4fc' }}>Free resource: {roadmap.resource}</a>
        </div>
      )}
    </div>
  )
}

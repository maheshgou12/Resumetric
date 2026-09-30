import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts'
import api from '../lib/api'

export default function ProgressPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['progress'],
    queryFn: () => api.get('/career/progress').then(r => r.data),
  })

  if (isLoading) return <div style={{ padding: '2rem' }}>Loading progress...</div>

  const matchTrend = (data?.match_trend || [])
    .filter(x => x.match != null)
    .map((x, i) => ({ name: `A${i + 1}`, match: x.match, ats: x.ats }))
  const resumeTrend = (data?.resume_trend || []).map(x => ({ name: `${x.name} v${x.version}`, score: x.score }))

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      <h1 style={{ fontSize: '1.875rem' }}>Progress Tracker</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
        {data?.resumes ?? 0} resumes · {data?.analyses ?? 0} job analyses. Re-upload after each fix and watch scores climb.
      </p>

      <div className="card">
        <h3>Resume 100-pt score across versions</h3>
        {resumeTrend.length === 0 ? <p style={{ color: '#64748b' }}>Upload resumes to see your trend.</p> : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={resumeTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,.1)' }} />
              <Bar dataKey="score" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3>Job match / ATS trend</h3>
        {matchTrend.length === 0 ? <p style={{ color: '#64748b' }}>Run job analyses to see your trend.</p> : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={matchTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,.1)' }} />
              <Legend />
              <Line type="monotone" dataKey="match" stroke="#6366f1" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ats" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts'
import api from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

function StatusBadge({ status }) {
  const config = {
    completed: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', label: '✓ Complete' },
    processing: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', label: '⟳ Processing' },
    pending: { color: '#6366f1', bg: 'rgba(99,102,241,0.1)', label: '⏳ Pending' },
    failed: { color: '#ef4444', bg: 'rgba(239,68,68,0.1)', label: '✗ Failed' },
  }
  const c = config[status] || config.pending
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', padding: '0.25rem 0.625rem',
      borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600,
      color: c.color, background: c.bg,
    }}>{c.label}</span>
  )
}

function ScorePill({ score }) {
  if (score === null || score === undefined) return <span style={{ color: '#475569', fontSize: '0.875rem' }}>—</span>
  const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'
  return <span style={{ fontWeight: 700, color, fontSize: '0.9375rem' }}>{score.toFixed(0)}%</span>
}

function SkeletonRow() {
  return (
    <tr>
      {[1, 2, 3, 4, 5, 6].map(i => (
        <td key={i}><div className="skeleton" style={{ height: 16, borderRadius: 4 }} /></td>
      ))}
    </tr>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '0.625rem', padding: '0.75rem', fontSize: '0.8125rem',
    }}>
      <div style={{ color: '#64748b', marginBottom: '0.375rem' }}>{label}</div>
      {payload.map(p => (
        <div key={p.dataKey} style={{ color: p.color, fontWeight: 600 }}>
          {p.name}: {p.value}%
        </div>
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()

  const { data: analyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['analyses'],
    queryFn: () => api.get('/analysis/?limit=30').then(r => r.data),
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['userStats'],
    queryFn: () => api.get('/users/me/stats').then(r => r.data),
  })

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', marginBottom: '0.375rem' }}>
            Welcome back, {user?.full_name?.split(' ')[0]}! 👋
          </h1>
          <p style={{ color: '#64748b' }}>Track your resume performance and analysis history</p>
        </div>
        <Link to="/analyze" className="btn-primary">⚡ New Analysis</Link>
      </div>

      {/* Email verification banner */}
      {user && !user.is_verified && (
        <div className="banner-warning" style={{ marginBottom: '1.5rem' }}>
          ✉️ Please verify your email address to unlock all features.
          {' '}<button
            style={{ background: 'none', border: 'none', color: '#fcd34d', cursor: 'pointer', textDecoration: 'underline', padding: 0 }}
            onClick={async () => {
              try {
                await api.post('/auth/resend-verification')
                toast.success('Verification link sent! Check the server console in local mode.')
              } catch {
                toast.error('Could not resend verification email')
              }
            }}
          >Resend verification email</button>
        </div>
      )}

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {[
          {
            label: 'Total Analyses',
            value: statsLoading ? '—' : stats?.total_analyses ?? 0,
            icon: '📊', color: '#6366f1',
          },
          {
            label: 'Avg Match Score',
            value: statsLoading ? '—' : `${stats?.avg_match_score ?? 0}%`,
            icon: '🎯', color: '#10b981',
          },
          {
            label: 'Avg ATS Score',
            value: statsLoading ? '—' : `${stats?.avg_ats_score ?? 0}%`,
            icon: '🤖', color: '#f59e0b',
          },
          {
            label: 'Best Match',
            value: statsLoading ? '—' : `${stats?.best_match_score?.toFixed(0) ?? 0}%`,
            icon: '🏆', color: '#ec4899',
          },
          {
            label: 'This Month',
            value: statsLoading ? '—' : `${stats?.analyses_this_month ?? 0} / ${stats?.monthly_limit ?? 5}`,
            icon: '📅', color: '#8b5cf6',
          },
        ].map(card => (
          <div key={card.label} className="card card-hover" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: 48, height: 48, borderRadius: '0.75rem', flexShrink: 0,
              background: `${card.color}20`, display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: '1.25rem',
            }}>{card.icon}</div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-display)', color: card.color }}>
                {statsLoading ? <div className="skeleton" style={{ width: 60, height: 24 }} /> : card.value}
              </div>
              <div style={{ fontSize: '0.8125rem', color: '#64748b', marginTop: 2 }}>{card.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions — jump to every CareerLens tool */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem', marginBottom: '2rem' }}>
        {[
          { to: '/career', icon: '🔍', label: '100-pt Score' },
          { to: '/resumes', icon: '📁', label: 'Resume Library' },
          { to: '/progress', icon: '📈', label: 'Progress' },
          { to: '/roadmaps', icon: '🗺️', label: 'Roadmaps' },
          { to: '/interview', icon: '🎤', label: 'Interview Prep' },
        ].map(a => (
          <Link key={a.to} to={a.to} className="card card-hover" style={{ textDecoration: 'none', textAlign: 'center', padding: '1rem 0.5rem' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.375rem' }}>{a.icon}</div>
            <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#cbd5e1' }}>{a.label}</div>
          </Link>
        ))}
      </div>

      {/* Trend Chart */}
      {stats?.trend?.length > 1 && (        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1.25rem' }}>📈 Score Trend</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={stats.trend} margin={{ left: -10, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#64748b' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#64748b' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '0.8125rem', color: '#94a3b8' }} />
              <Line
                type="monotone" dataKey="match_score" name="Match Score"
                stroke="#6366f1" strokeWidth={2} dot={{ r: 4, fill: '#6366f1' }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone" dataKey="ats_score" name="ATS Score"
                stroke="#10b981" strokeWidth={2} dot={{ r: 4, fill: '#10b981' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Analysis History Table */}
      <div>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1rem' }}>📋 Analysis History</h2>

        {analysesLoading ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  {['Date', 'Resume', 'Job Title', 'Match', 'ATS', 'Status', 'Actions'].map(h => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map(i => <SkeletonRow key={i} />)}
              </tbody>
            </table>
          </div>
        ) : !analyses?.length ? (
          <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📄</div>
            <h3 style={{ marginBottom: '0.75rem' }}>No analyses yet</h3>
            <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Upload your resume to get your first AI-powered analysis</p>
            <Link to="/analyze" className="btn-primary">⚡ Start Analyzing</Link>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Resume</th>
                  <th>Job Title</th>
                  <th>Match</th>
                  <th>ATS</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map(a => (
                  <tr key={a.id}>
                    <td style={{ color: '#64748b', whiteSpace: 'nowrap' }}>
                      {a.created_at ? format(new Date(a.created_at), 'MMM d, yyyy') : '—'}
                    </td>
                    <td>
                      <span style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                        {a.resume_filename || 'resume'}
                      </span>
                    </td>
                    <td>
                      {a.job_title ? (
                        <div>
                          <div style={{ color: '#e2e8f0', fontWeight: 500 }}>{a.job_title}</div>
                          {a.company_name && <div style={{ color: '#475569', fontSize: '0.75rem' }}>{a.company_name}</div>}
                        </div>
                      ) : <span style={{ color: '#475569' }}>—</span>}
                    </td>
                    <td><ScorePill score={a.match_score} /></td>
                    <td><ScorePill score={a.ats_score} /></td>
                    <td><StatusBadge status={a.status} /></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.375rem' }}>
                        <Link
                          to={`/analysis/${a.id}`}
                          style={{
                            padding: '0.25rem 0.625rem', borderRadius: '0.375rem',
                            background: 'rgba(99,102,241,0.1)', color: '#a5b4fc',
                            textDecoration: 'none', fontSize: '0.75rem', fontWeight: 600,
                          }}
                        >
                          View
                        </Link>
                        {a.report_url && (
                          <a
                            href={a.report_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              padding: '0.25rem 0.625rem', borderRadius: '0.375rem',
                              background: 'rgba(16,185,129,0.1)', color: '#34d399',
                              textDecoration: 'none', fontSize: '0.75rem', fontWeight: 600,
                            }}
                          >
                            ⬇ PDF
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

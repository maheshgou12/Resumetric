import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line, Legend
} from 'recharts'
import api from '../lib/api'
import { format } from 'date-fns'

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
          {p.name}: {p.value}
        </div>
      ))}
    </div>
  )
}

function StatCard({ icon, label, value, color, loading }) {
  return (
    <div className="card card-hover" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{
        width: 52, height: 52, borderRadius: '0.875rem', flexShrink: 0,
        background: `${color}20`, display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize: '1.375rem',
      }}>{icon}</div>
      <div>
        {loading
          ? <div className="skeleton" style={{ width: 80, height: 28, marginBottom: 6 }} />
          : <div style={{ fontSize: '1.875rem', fontWeight: 800, fontFamily: 'var(--font-display)', color, lineHeight: 1 }}>{value}</div>
        }
        <div style={{ fontSize: '0.8125rem', color: '#64748b', marginTop: 4 }}>{label}</div>
      </div>
    </div>
  )
}

export default function AdminDashboardPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['adminStats'],
    queryFn: () => api.get('/admin/stats').then(r => r.data),
  })

  const { data: missingSkills, isLoading: skillsLoading } = useQuery({
    queryKey: ['adminMissingSkills'],
    queryFn: () => api.get('/admin/missing-skills?limit=12').then(r => r.data),
  })

  const { data: signupTrend, isLoading: trendLoading } = useQuery({
    queryKey: ['adminSignupTrend'],
    queryFn: () => api.get('/admin/signup-trend?days=30').then(r => r.data),
  })

  const { data: analyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['adminAnalyses', search, statusFilter],
    queryFn: () => api.get(`/admin/analyses?search=${search}&status_filter=${statusFilter}&limit=50`).then(r => r.data),
  })

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['adminUsers', search],
    queryFn: () => api.get(`/admin/users?search=${search}&limit=50`).then(r => r.data),
    enabled: activeTab === 'users',
  })

  const TAB_STYLE = (active) => ({
    padding: '0.625rem 1.25rem', borderRadius: '0.625rem',
    border: 'none', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600,
    transition: 'all 0.15s',
    background: active ? 'rgba(99,102,241,0.15)' : 'transparent',
    color: active ? '#a5b4fc' : '#64748b',
  })

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <div style={{
            padding: '0.25rem 0.75rem', borderRadius: '9999px',
            background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)',
            fontSize: '0.75rem', fontWeight: 700, color: '#fbbf24', letterSpacing: '0.05em',
          }}>ADMIN</div>
          <h1 style={{ fontSize: '1.875rem' }}>Analytics Dashboard</h1>
        </div>
        <p style={{ color: '#64748b' }}>Platform-wide usage, top missing skills, and user management</p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <StatCard icon="👥" label="Total Users" value={stats?.total_users ?? '—'} color="#6366f1" loading={statsLoading} />
        <StatCard icon="📊" label="Total Analyses" value={stats?.total_analyses ?? '—'} color="#10b981" loading={statsLoading} />
        <StatCard icon="🎯" label="Avg Match Score" value={stats ? `${stats.avg_match_score}%` : '—'} color="#f59e0b" loading={statsLoading} />
        <StatCard icon="🤖" label="Avg ATS Score" value={stats ? `${stats.avg_ats_score}%` : '—'} color="#8b5cf6" loading={statsLoading} />
        <StatCard icon="🆕" label="New Users (30d)" value={stats?.new_users_30d ?? '—'} color="#06b6d4" loading={statsLoading} />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '2rem' }}>
        {/* Missing Skills Bar Chart */}
        <div className="card">
          <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1.25rem' }}>🔥 Top Missing Skills Platform-wide</h2>
          {skillsLoading ? (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div className="animate-spin" style={{ width: 32, height: 32, borderRadius: '50%', border: '3px solid rgba(99,102,241,0.2)', borderTop: '3px solid #6366f1' }} />
            </div>
          ) : missingSkills?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={missingSkills} layout="vertical" margin={{ left: 0, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis dataKey="skill" type="category" tick={{ fontSize: 11, fill: '#94a3b8' }} width={90} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', flexDirection: 'column', gap: '0.5rem' }}>
              <span style={{ fontSize: '2rem' }}>📊</span>
              <span>No skill data yet</span>
            </div>
          )}
        </div>

        {/* Signup Trend Line Chart */}
        <div className="card">
          <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1.25rem' }}>📈 New Signups (Last 30 Days)</h2>
          {trendLoading ? (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div className="animate-spin" style={{ width: 32, height: 32, borderRadius: '50%', border: '3px solid rgba(99,102,241,0.2)', borderTop: '3px solid #6366f1' }} />
            </div>
          ) : signupTrend?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={signupTrend} margin={{ left: -20, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={d => d.slice(5)} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone" dataKey="signups" name="Signups"
                  stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: '#10b981' }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', flexDirection: 'column', gap: '0.5rem' }}>
              <span style={{ fontSize: '2rem' }}>📉</span>
              <span>No signup data yet</span>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '1.25rem', background: 'rgba(255,255,255,0.03)', padding: '0.25rem', borderRadius: '0.75rem', width: 'fit-content' }}>
        {['overview', 'analyses', 'users'].map(tab => (
          <button key={tab} style={TAB_STYLE(activeTab === tab)} onClick={() => setActiveTab(tab)}>
            {tab === 'overview' ? '📊 Overview' : tab === 'analyses' ? '📋 All Analyses' : '👥 Users'}
          </button>
        ))}
      </div>

      {/* Search & Filter */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <input
          className="input"
          placeholder={activeTab === 'users' ? 'Search by name or email...' : 'Search by user, job title...'}
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ maxWidth: 320 }}
        />
        {activeTab === 'analyses' && (
          <select
            className="input"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            style={{ maxWidth: 180 }}
          >
            <option value="">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        )}
      </div>

      {/* Analyses Table */}
      {(activeTab === 'overview' || activeTab === 'analyses') && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>User</th>
                <th>Job Title</th>
                <th>Company</th>
                <th>Match</th>
                <th>ATS</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {analysesLoading ? (
                [1, 2, 3, 4, 5].map(i => (
                  <tr key={i}>
                    {[1, 2, 3, 4, 5, 6, 7].map(j => (
                      <td key={j}><div className="skeleton" style={{ height: 14, borderRadius: 4 }} /></td>
                    ))}
                  </tr>
                ))
              ) : !analyses?.length ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#475569' }}>
                    No analyses found
                  </td>
                </tr>
              ) : (
                analyses.map(a => (
                  <tr key={a.id}>
                    <td style={{ color: '#64748b', whiteSpace: 'nowrap', fontSize: '0.8125rem' }}>
                      {a.created_at ? format(new Date(a.created_at), 'MMM d, yy') : '—'}
                    </td>
                    <td>
                      <div style={{ fontWeight: 500, color: '#e2e8f0', fontSize: '0.875rem' }}>{a.user_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#475569' }}>{a.user_email}</div>
                    </td>
                    <td style={{ color: '#94a3b8', fontSize: '0.875rem' }}>{a.job_title || '—'}</td>
                    <td style={{ color: '#64748b', fontSize: '0.8125rem' }}>{a.company_name || '—'}</td>
                    <td>
                      {a.match_score != null
                        ? <span style={{ fontWeight: 700, color: a.match_score >= 75 ? '#10b981' : a.match_score >= 50 ? '#f59e0b' : '#ef4444' }}>{a.match_score.toFixed(0)}%</span>
                        : <span style={{ color: '#475569' }}>—</span>
                      }
                    </td>
                    <td>
                      {a.ats_score != null
                        ? <span style={{ fontWeight: 700, color: a.ats_score >= 75 ? '#10b981' : a.ats_score >= 50 ? '#f59e0b' : '#ef4444' }}>{a.ats_score.toFixed(0)}%</span>
                        : <span style={{ color: '#475569' }}>—</span>
                      }
                    </td>
                    <td>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', padding: '0.2rem 0.5rem',
                        borderRadius: '9999px', fontSize: '0.7rem', fontWeight: 700,
                        background: a.status === 'completed' ? 'rgba(16,185,129,0.1)' : a.status === 'failed' ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)',
                        color: a.status === 'completed' ? '#10b981' : a.status === 'failed' ? '#ef4444' : '#f59e0b',
                      }}>
                        {a.status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Users Table */}
      {activeTab === 'users' && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Verified</th>
                <th>This Month</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {usersLoading ? (
                [1, 2, 3, 4, 5].map(i => (
                  <tr key={i}>
                    {[1, 2, 3, 4, 5, 6].map(j => (
                      <td key={j}><div className="skeleton" style={{ height: 14, borderRadius: 4 }} /></td>
                    ))}
                  </tr>
                ))
              ) : !users?.length ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#475569' }}>No users found</td>
                </tr>
              ) : (
                users.map(u => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <div style={{
                          width: 30, height: 30, borderRadius: '50%',
                          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '0.75rem', fontWeight: 700, color: 'white', flexShrink: 0,
                        }}>
                          {u.full_name?.[0]?.toUpperCase()}
                        </div>
                        <span style={{ fontWeight: 500, color: '#e2e8f0', fontSize: '0.875rem' }}>{u.full_name}</span>
                      </div>
                    </td>
                    <td style={{ color: '#64748b', fontSize: '0.8125rem' }}>{u.email}</td>
                    <td>
                      <span style={{
                        padding: '0.2rem 0.5rem', borderRadius: '9999px',
                        fontSize: '0.7rem', fontWeight: 700,
                        background: u.role === 'admin' ? 'rgba(251,191,36,0.1)' : 'rgba(99,102,241,0.1)',
                        color: u.role === 'admin' ? '#fbbf24' : '#a5b4fc',
                      }}>
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: u.is_verified ? '#10b981' : '#ef4444', fontSize: '0.875rem' }}>
                        {u.is_verified ? '✓' : '✗'}
                      </span>
                    </td>
                    <td style={{ color: '#94a3b8', fontSize: '0.875rem' }}>{u.analyses_this_month}</td>
                    <td style={{ color: '#64748b', fontSize: '0.8125rem', whiteSpace: 'nowrap' }}>
                      {u.created_at ? format(new Date(u.created_at), 'MMM d, yyyy') : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

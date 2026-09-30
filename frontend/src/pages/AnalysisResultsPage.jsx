import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  PolarAngleAxis
} from 'recharts'
import api from '../lib/api'
import toast from 'react-hot-toast'

// ─── Score Ring ────────────────────────────────────────────────────────────
function ScoreRing({ score, label, color, size = 120 }) {
  const data = [{ value: score, fill: color }]
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ width: size, height: size, position: 'relative', margin: '0 auto' }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            innerRadius="70%" outerRadius="100%"
            barSize={10} data={data}
            startAngle={90} endAngle={-270}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
            <RadialBar
              background={{ fill: 'rgba(255,255,255,0.04)' }}
              dataKey="value" angleAxisId={0}
              cornerRadius={5}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div style={{
          position: 'absolute', inset: 0, display: 'flex',
          flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: size < 100 ? '1.25rem' : '1.75rem', fontWeight: 800, color, fontFamily: 'var(--font-display)', lineHeight: 1 }}>
            {score?.toFixed(0) ?? '--'}
          </span>
          <span style={{ fontSize: '0.625rem', color: '#64748b', fontWeight: 500 }}>/ 100</span>
        </div>
      </div>
      <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', fontWeight: 600, color: '#94a3b8' }}>{label}</div>
    </div>
  )
}

// ─── Skill Tag ─────────────────────────────────────────────────────────────
function SkillTag({ skill, type }) {
  const styles = {
    matched: { background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.2)' },
    missing: { background: 'rgba(239,68,68,0.1)', color: '#f87171', border: '1px solid rgba(239,68,68,0.2)' },
  }
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
      padding: '0.25rem 0.625rem', borderRadius: '9999px', fontSize: '0.8125rem', fontWeight: 500,
      ...styles[type],
    }}>
      {type === 'matched' ? '✓' : '✗'} {skill}
    </span>
  )
}

// ─── Skeleton ──────────────────────────────────────────────────────────────
function AnalysisSkeleton() {
  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2.5rem 1.5rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {[1, 2, 3].map(i => (
          <div key={i} className="card" style={{ height: 160 }}>
            <div className="skeleton" style={{ width: 80, height: 80, borderRadius: '50%', margin: '0 auto 12px' }} />
            <div className="skeleton" style={{ width: '60%', height: 14, margin: '0 auto' }} />
          </div>
        ))}
      </div>
      {[1, 2, 3].map(i => (
        <div key={i} className="card" style={{ marginBottom: '1rem' }}>
          <div className="skeleton" style={{ width: '30%', height: 20, marginBottom: '1rem' }} />
          <div className="skeleton" style={{ width: '100%', height: 14, marginBottom: '0.5rem' }} />
          <div className="skeleton" style={{ width: '80%', height: 14 }} />
        </div>
      ))}
    </div>
  )
}

// ─── Chat Panel ────────────────────────────────────────────────────────────
function ChatPanel({ analysisId }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "👋 Hi! I'm your AI career coach. Ask me anything about your resume or how to improve it for this role." }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(m => [...m, { role: 'user', text: userMsg }])
    setLoading(true)
    try {
      const resp = await api.post(`/analysis/${analysisId}/chat`, { message: userMsg })
      setMessages(m => [...m, { role: 'assistant', text: resp.data.reply }])
    } catch {
      setMessages(m => [...m, { role: 'assistant', text: 'Sorry, I encountered an error. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 400 }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>🤖</span> AI Rewrite Coach
      </h3>
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem', paddingRight: '0.5rem' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              maxWidth: '85%', padding: '0.625rem 1rem', borderRadius: '1rem',
              fontSize: '0.875rem', lineHeight: 1.5,
              background: msg.role === 'user' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.05)',
              color: msg.role === 'user' ? 'white' : '#cbd5e1',
              borderBottomRightRadius: msg.role === 'user' ? '0.25rem' : '1rem',
              borderBottomLeftRadius: msg.role === 'assistant' ? '0.25rem' : '1rem',
            }}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.75rem 1rem', borderRadius: '1rem', borderBottomLeftRadius: '0.25rem' }}>
              <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                {[0, 1, 2].map(i => (
                  <div key={i} style={{
                    width: 6, height: 6, borderRadius: '50%', background: '#6366f1',
                    animation: 'pulse-glow 1.4s infinite',
                    animationDelay: `${i * 0.2}s`,
                  }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          className="input"
          placeholder="Ask about your resume..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          style={{ flex: 1 }}
        />
        <button className="btn-primary" onClick={send} disabled={loading || !input.trim()} style={{ padding: '0.75rem 1rem' }}>
          →
        </button>
      </div>
    </div>
  )
}

// ─── Main Results Page ─────────────────────────────────────────────────────
export default function AnalysisResultsPage() {
  const { id } = useParams()
  const [coverLetter, setCoverLetter] = useState('')
  const [generatingCL, setGeneratingCL] = useState(false)

  const { data: analysis, isLoading, error, refetch } = useQuery({
    queryKey: ['analysis', id],
    queryFn: () => api.get(`/analysis/${id}`).then(r => r.data),
    refetchInterval: (data) => {
      if (!data?.state?.data) return 3000
      return data.state.data.status === 'processing' || data.state.data.status === 'pending' ? 2000 : false
    },
  })

  const generateCoverLetter = async () => {
    setGeneratingCL(true)
    try {
      const resp = await api.post(`/analysis/${id}/cover-letter`)
      setCoverLetter(resp.data.cover_letter)
    } catch {
      toast.error('Could not generate cover letter')
    } finally {
      setGeneratingCL(false)
    }
  }

  const [downloading, setDownloading] = useState(false)
  const downloadReport = async () => {
    // Prefer the stored S3 link when present, else regenerate on demand.
    if (analysis.report_url) {
      window.open(analysis.report_url, '_blank', 'noopener')
      return
    }
    setDownloading(true)
    try {
      const resp = await api.get(`/analysis/${id}/report`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `careerlens-report-${id.slice(0, 8)}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Report downloaded!')
    } catch {
      toast.error('Could not download report yet')
    } finally {
      setDownloading(false)
    }
  }

  if (isLoading) return <AnalysisSkeleton />
  if (error) return (
    <div style={{ maxWidth: 600, margin: '4rem auto', textAlign: 'center', padding: '2rem' }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>😕</div>
      <h2 style={{ marginBottom: '0.75rem' }}>Analysis not found</h2>
      <Link to="/analyze" className="btn-primary">← New Analysis</Link>
    </div>
  )

  const isPending = analysis.status === 'pending' || analysis.status === 'processing'

  const matchColor = analysis.match_score >= 75 ? '#10b981' : analysis.match_score >= 50 ? '#f59e0b' : '#ef4444'
  const atsColor = analysis.ats_score >= 75 ? '#10b981' : analysis.ats_score >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <div style={{ maxWidth: 980, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <Link to="/dashboard" style={{ color: '#64748b', textDecoration: 'none', fontSize: '0.875rem', display: 'inline-flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.75rem' }}>
            ← Back to Dashboard
          </Link>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.375rem' }}>
            Analysis Results
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9375rem' }}>
            {analysis.job_title && <strong style={{ color: '#94a3b8' }}>{analysis.job_title}</strong>}
            {analysis.company_name && <span> at {analysis.company_name}</span>}
            {analysis.resume_filename && (
              <span style={{ marginLeft: 8 }}>
                • <span style={{ color: '#475569' }}>{analysis.resume_filename}</span>
              </span>
            )}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          {!isPending && analysis.status === 'completed' && (
            <button onClick={downloadReport} className="btn-primary" disabled={downloading}>
              {downloading ? 'Preparing...' : '⬇️ Download Report'}
            </button>
          )}
          <Link to="/analyze" className="btn-secondary">⚡ New Analysis</Link>
        </div>
      </div>

      {/* Email sent notification */}
      {analysis.report_emailed && (
        <div className="banner-warning" style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', color: '#34d399', marginBottom: '1.5rem' }}>
          📬 Report emailed to your inbox
        </div>
      )}

      {/* Unverified email banner */}
      {!isPending && (
        <>
          {/* Processing state */}
        </>
      )}

      {isPending ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <div className="animate-spin" style={{
            width: 64, height: 64, borderRadius: '50%',
            border: '4px solid rgba(99,102,241,0.2)',
            borderTop: '4px solid #6366f1',
            margin: '0 auto 1.5rem',
          }} />
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem' }}>
            {analysis.status === 'pending' ? '⏳ Queued for Analysis' : '🤖 AI is Analyzing...'}
          </h3>
          <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
            Running TF-IDF scoring, ATS checks, and generating personalized feedback...
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: 300, margin: '0 auto' }}>
            {['Extracting resume content', 'Computing match score', 'Checking ATS compatibility', 'Generating AI feedback', 'Creating PDF report'].map((step, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem', color: '#64748b' }}>
                <div className="animate-spin" style={{ width: 12, height: 12, borderRadius: '50%', border: '2px solid rgba(99,102,241,0.2)', borderTop: '2px solid #6366f1', flexShrink: 0 }} />
                {step}
              </div>
            ))}
          </div>
        </div>
      ) : analysis.status === 'failed' ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
          <h3 style={{ marginBottom: '0.75rem' }}>Analysis Failed</h3>
          <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>{analysis.error_message || 'An unexpected error occurred.'}</p>
          <Link to="/analyze" className="btn-primary">Try Again</Link>
        </div>
      ) : (
        <>
          {/* Score Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="card" style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
              <ScoreRing score={analysis.match_score} label="Match Score" color={matchColor} />
            </div>
            <div className="card" style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
              <ScoreRing score={analysis.ats_score} label="ATS Score" color={atsColor} />
            </div>
            <div className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#6366f1', fontFamily: 'var(--font-display)', marginBottom: '0.25rem' }}>
                {analysis.matched_skills?.length ?? 0}
              </div>
              <div style={{ fontSize: '0.8125rem', color: '#64748b', fontWeight: 600 }}>Skills Matched</div>
              <div style={{ marginTop: '1rem', height: 4, background: 'rgba(99,102,241,0.15)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{
                  height: '100%', borderRadius: 2, background: '#6366f1',
                  width: `${Math.min(100, ((analysis.matched_skills?.length ?? 0) / Math.max(1, (analysis.matched_skills?.length ?? 0) + (analysis.missing_skills?.length ?? 0))) * 100)}%`,
                }} />
              </div>
            </div>
            <div className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#ef4444', fontFamily: 'var(--font-display)', marginBottom: '0.25rem' }}>
                {analysis.missing_skills?.length ?? 0}
              </div>
              <div style={{ fontSize: '0.8125rem', color: '#64748b', fontWeight: 600 }}>Skills Missing</div>
            </div>
          </div>

          {/* CareerLens 100-pt Resume Score */}
          {analysis.feedback?.resume_score && (
            <div className="card" style={{ marginBottom: '1.25rem', borderTop: '2px solid #8b5cf6' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.25rem' }}>
                🔍 CareerLens Resume Score — {analysis.feedback.resume_score.overall}/100
                <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#a5b4fc' }}>
                  Grade {analysis.feedback.resume_score.grade}
                </span>
              </h3>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1rem' }}>{analysis.feedback.resume_score.verdict}</p>
              {Object.entries(analysis.feedback.resume_score.breakdown).map(([k, v]) => (
                <div key={k} style={{ margin: '0.5rem 0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', color: '#94a3b8' }}>
                    <span style={{ textTransform: 'capitalize' }}>{k}</span>
                    <span>{v.score}/{v.max}</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 99, background: 'rgba(255,255,255,0.08)', overflow: 'hidden', marginTop: 4 }}>
                    <div style={{ width: `${(v.score / v.max) * 100}%`, height: '100%', background: 'linear-gradient(90deg,#6366f1,#8b5cf6)' }} />
                  </div>
                </div>
              ))}
              {analysis.feedback.career_domains?.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#a5b4fc', marginBottom: '0.5rem' }}>Suitable career domains</div>
                  {analysis.feedback.career_domains.map(d => (
                    <div key={d.domain} style={{ fontSize: '0.8125rem', color: '#94a3b8', padding: '0.375rem 0', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                      <b style={{ color: '#e2e8f0' }}>{d.domain}</b> — {d.match_pct}% · Roles: {d.role_examples.join(', ')}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* AI Summary */}
          {analysis.feedback?.overall_summary && (
            <div className="card" style={{ marginBottom: '1.25rem', borderLeft: '3px solid #6366f1' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: '#a5b4fc' }}>🎯 Executive Summary</h3>
              <p style={{ color: '#cbd5e1', lineHeight: 1.7, fontSize: '0.9375rem' }}>{analysis.feedback.overall_summary}</p>
            </div>
          )}

          {/* Priority Action */}
          {analysis.feedback?.priority_action && (
            <div style={{
              background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: '0.875rem', padding: '1rem 1.25rem', marginBottom: '1.25rem',
              display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
            }}>
              <span style={{ fontSize: '1.25rem' }}>🎯</span>
              <div>
                <div style={{ fontWeight: 700, color: '#fcd34d', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Priority Action</div>
                <div style={{ color: '#fbbf24', fontSize: '0.9375rem', lineHeight: 1.6 }}>{analysis.feedback.priority_action}</div>
              </div>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          {(analysis.feedback?.strengths?.length > 0 || analysis.feedback?.weaknesses?.length > 0) && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
              <div className="card" style={{ borderTop: '2px solid #10b981' }}>
                <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#34d399', marginBottom: '0.875rem' }}>✓ Strengths</h3>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {analysis.feedback.strengths.map((s, i) => (
                    <li key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', fontSize: '0.875rem', color: '#94a3b8', lineHeight: 1.5 }}>
                      <span style={{ color: '#10b981', flexShrink: 0, marginTop: 1 }}>•</span> {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="card" style={{ borderTop: '2px solid #ef4444' }}>
                <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#f87171', marginBottom: '0.875rem' }}>⚠ Areas to Improve</h3>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {analysis.feedback.weaknesses.map((w, i) => (
                    <li key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', fontSize: '0.875rem', color: '#94a3b8', lineHeight: 1.5 }}>
                      <span style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }}>•</span> {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Skills */}
          <div className="card" style={{ marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>🔧 Skills Analysis</h3>
            {analysis.matched_skills?.length > 0 && (
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#34d399', marginBottom: '0.5rem' }}>
                  Matched ({analysis.matched_skills.length})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysis.matched_skills.map(s => <SkillTag key={s} skill={s} type="matched" />)}
                </div>
              </div>
            )}
            {analysis.missing_skills?.length > 0 && (
              <div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#f87171', marginBottom: '0.5rem' }}>
                  Missing ({analysis.missing_skills.length})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysis.missing_skills.map(s => <SkillTag key={s} skill={s} type="missing" />)}
                </div>
              </div>
            )}
          </div>

          {/* Suggestions */}
          {analysis.feedback?.suggestions?.length > 0 && (
            <div className="card" style={{ marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>💡 Improvement Suggestions</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {analysis.feedback.suggestions.map((s, i) => (
                  <div key={i} style={{
                    background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.15)',
                    borderRadius: '0.75rem', padding: '0.875rem 1rem',
                  }}>
                    <div style={{ fontWeight: 600, color: '#a5b4fc', fontSize: '0.8125rem', marginBottom: '0.25rem' }}>
                      {s.section}
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '0.875rem', lineHeight: 1.6 }}>{s.suggestion}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ATS Issues */}
          {analysis.feedback?.ats_issues?.length > 0 && (
            <div className="card" style={{ marginBottom: '1.25rem', borderTop: '2px solid #f59e0b' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: '#fbbf24' }}>📋 ATS Issues Found</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {analysis.feedback.ats_issues.map((issue, i) => (
                  <li key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.875rem', color: '#94a3b8' }}>
                    <span style={{ color: '#f59e0b' }}>⚠</span> {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Skill Roadmap */}
          {analysis.skill_roadmap?.length > 0 && (
            <div className="card" style={{ marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>🗺️ Skill Development Roadmap</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {analysis.skill_roadmap.map((item, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: '1rem',
                    background: 'rgba(255,255,255,0.02)', borderRadius: '0.75rem',
                    padding: '0.875rem', border: '1px solid rgba(255,255,255,0.05)',
                  }}>
                    <div style={{
                      width: 36, height: 36, borderRadius: '0.5rem',
                      background: item.priority === 'high' ? 'rgba(239,68,68,0.15)' : 'rgba(99,102,241,0.15)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '0.75rem', fontWeight: 700,
                      color: item.priority === 'high' ? '#f87171' : '#a5b4fc',
                      flexShrink: 0,
                    }}>
                      {i + 1}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, color: '#e2e8f0', fontSize: '0.9rem', marginBottom: '0.125rem' }}>
                        {item.skill}
                        <span style={{
                          marginLeft: '0.5rem', fontSize: '0.7rem', fontWeight: 600, padding: '0.1rem 0.375rem',
                          borderRadius: '9999px',
                          background: item.priority === 'high' ? 'rgba(239,68,68,0.1)' : 'rgba(99,102,241,0.1)',
                          color: item.priority === 'high' ? '#f87171' : '#a5b4fc',
                        }}>
                          {item.priority?.toUpperCase()}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.8125rem', color: '#64748b' }}>{item.resource}</div>
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: '#475569', flexShrink: 0 }}>{item.time}</div>
                    <a href={item.url} target="_blank" rel="noopener noreferrer" className="btn-ghost" style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem', flexShrink: 0 }}>
                      Learn →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Coach & Cover Letter */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
            <ChatPanel analysisId={id} />
            <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>📝</span> Cover Letter Generator
              </h3>
              {!coverLetter ? (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '1rem' }}>
                  <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✉️</div>
                  <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
                    Generate a personalized cover letter tailored to this specific job posting.
                  </p>
                  <button className="btn-primary" onClick={generateCoverLetter} disabled={generatingCL} style={{ justifyContent: 'center' }}>
                    {generatingCL ? (
                      <span className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', display: 'inline-block' }} />
                    ) : '✨'} Generate Cover Letter
                  </button>
                </div>
              ) : (
                <div style={{ flex: 1, overflowY: 'auto' }}>
                  <pre style={{
                    whiteSpace: 'pre-wrap', fontFamily: 'var(--font-sans)', fontSize: '0.8125rem',
                    color: '#cbd5e1', lineHeight: 1.7, margin: 0,
                  }}>{coverLetter}</pre>
                  <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn-secondary"
                      style={{ fontSize: '0.8125rem', padding: '0.5rem 1rem' }}
                      onClick={() => { navigator.clipboard.writeText(coverLetter); toast.success('Copied!') }}
                    >
                      📋 Copy
                    </button>
                    <button className="btn-ghost" style={{ fontSize: '0.8125rem', padding: '0.5rem 1rem' }} onClick={() => setCoverLetter('')}>
                      ↺ Regenerate
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

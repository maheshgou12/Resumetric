import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { useAuth } from '../context/AuthContext'

const MAX_SIZE = 5 * 1024 * 1024 // 5MB

export default function AnalyzePage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState('')

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const err = rejectedFiles[0].errors[0]
      if (err.code === 'file-too-large') toast.error('File too large. Max 5MB.')
      else if (err.code === 'file-invalid-type') toast.error('Only PDF and DOCX files are supported.')
      else toast.error(err.message)
      return
    }
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxSize: MAX_SIZE,
    maxFiles: 1,
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return toast.error('Please upload your resume')
    if (!jobDescription.trim()) return toast.error('Please enter a job description')

    setLoading(true)
    setProgress('Uploading resume...')

    const formData = new FormData()
    formData.append('resume', file)
    formData.append('job_description', jobDescription)
    formData.append('job_title', jobTitle)
    formData.append('company_name', companyName)

    try {
      setProgress('Extracting text and running AI analysis...')
      const resp = await api.post('/analysis/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('Analysis started! 🚀')
      navigate(`/analysis/${resp.data.id}`)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Analysis failed. Please try again.'
      toast.error(msg)
    } finally {
      setLoading(false)
      setProgress('')
    }
  }

  const usedThisMonth = user?.analyses_this_month || 0

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
          ⚡ Analyze Your Resume
        </h1>
        <p style={{ color: '#64748b', fontSize: '1rem' }}>
          Upload your resume and paste a job description to get your AI-powered analysis.
        </p>

        {/* Usage indicator */}
        {user && (
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            marginTop: '0.75rem',
            background: 'rgba(16,185,129,0.1)',
            border: '1px solid rgba(16,185,129,0.2)',
            borderRadius: '9999px', padding: '0.375rem 0.875rem',
            fontSize: '0.8125rem', fontWeight: 500,
            color: '#34d399',
          }}>
            ✅ {usedThisMonth} {usedThisMonth === 1 ? 'analysis' : 'analyses'} this month • Unlimited
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Resume Upload */}
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{
              width: 28, height: 28, borderRadius: '0.5rem',
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.75rem', fontWeight: 700, color: 'white',
            }}>1</span>
            Upload Resume
          </h2>

          {!file ? (
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📄</div>
              <p style={{ color: '#e2e8f0', fontWeight: 600, marginBottom: '0.5rem' }}>
                {isDragActive ? 'Drop it here!' : 'Drag & drop your resume here'}
              </p>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1rem' }}>
                or click to browse files
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                {['PDF', 'DOCX', 'DOC'].map(ext => (
                  <span key={ext} className="tag tag-purple">{ext}</span>
                ))}
                <span className="tag tag-amber">Max 5MB</span>
              </div>
            </div>
          ) : (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '1rem',
              padding: '1rem', background: 'rgba(99,102,241,0.08)',
              border: '1px solid rgba(99,102,241,0.2)', borderRadius: '0.75rem',
            }}>
              <div style={{
                width: 48, height: 48, borderRadius: '0.625rem',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.25rem', flexShrink: 0,
              }}>📄</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, color: '#e2e8f0', marginBottom: '0.25rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {file.name}
                </div>
                <div style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                  {(file.size / 1024).toFixed(0)} KB
                </div>
              </div>
              <button
                type="button"
                onClick={() => setFile(null)}
                style={{
                  background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
                  borderRadius: '0.5rem', padding: '0.375rem 0.75rem',
                  color: '#f87171', cursor: 'pointer', fontSize: '0.8125rem', fontWeight: 500,
                }}
              >
                ✕ Remove
              </button>
            </div>
          )}
        </div>

        {/* Job Description */}
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{
              width: 28, height: 28, borderRadius: '0.5rem',
              background: 'linear-gradient(135deg, #10b981, #059669)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.75rem', fontWeight: 700, color: 'white',
            }}>2</span>
            Job Details
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Job Title <span style={{ color: '#475569' }}>(optional)</span>
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g. Senior React Developer"
                value={jobTitle}
                onChange={e => setJobTitle(e.target.value)}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Company Name <span style={{ color: '#475569' }}>(optional)</span>
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g. Acme Corp"
                value={companyName}
                onChange={e => setCompanyName(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
              Job Description <span style={{ color: '#ef4444' }}>*</span>
              <button
                type="button"
                onClick={() => setJobDescription('Backend Developer at FinTech Co.\n\nRequirements: Python, FastAPI, PostgreSQL, Docker, AWS, Kubernetes, Microservices, REST API, CI/CD.\n2+ years experience building scalable APIs with 99.9% uptime.\nMust have: Git, Agile, SQL, strong testing practices.\nNice to have: Terraform, Kafka, React.')}
                style={{ background: 'none', border: 'none', color: '#6366f1', cursor: 'pointer', fontSize: '0.75rem', marginLeft: '0.5rem', textDecoration: 'underline' }}
              >
                Try a sample JD
              </button>
            </label>
            <textarea
              className="input"
              placeholder="Paste the full job description here. The more detail you provide, the more accurate the analysis will be..."
              value={jobDescription}
              onChange={e => setJobDescription(e.target.value)}
              style={{ minHeight: 200 }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#475569' }}>
                Include requirements, responsibilities, and skills sections for best results
              </span>
              <span style={{ fontSize: '0.75rem', color: jobDescription.length > 100 ? '#34d399' : '#64748b' }}>
                {jobDescription.length} chars
              </span>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !file || !jobDescription.trim()}
            style={{ fontSize: '1rem', padding: '0.875rem 2rem' }}
          >
            {loading ? (
              <>
                <span className="animate-spin" style={{ width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', display: 'inline-block' }} />
                {progress || 'Analyzing...'}
              </>
            ) : (
              <> ⚡ Analyze My Resume</>
            )}
          </button>

          {loading && (
            <div style={{ flex: 1 }}>
              <div style={{ marginBottom: '0.375rem', fontSize: '0.8125rem', color: '#64748b' }}>{progress}</div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: '70%',
                    background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
                    animation: 'shimmer 1.5s infinite',
                    backgroundSize: '200% 100%',
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  )
}

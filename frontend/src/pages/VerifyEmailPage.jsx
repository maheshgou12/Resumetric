import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function VerifyEmailPage() {
  const navigate = useNavigate()
  const token = new URLSearchParams(window.location.search).get('token')

  useEffect(() => {
    if (!token) {
      toast.error('Invalid verification link')
      navigate('/dashboard')
      return
    }
    api.get(`/auth/verify-email?token=${token}`)
      .then(() => {
        toast.success('Email verified! ✅')
        navigate('/dashboard')
      })
      .catch((err) => {
        toast.error(err.response?.data?.detail || 'Verification failed or link expired')
        navigate('/dashboard')
      })
  }, [token, navigate])

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: '#0f172a',
    }}>
      <div style={{ textAlign: 'center' }}>
        <div className="animate-spin" style={{
          width: 48, height: 48, borderRadius: '50%',
          border: '3px solid rgba(99,102,241,0.2)', borderTop: '3px solid #6366f1',
          margin: '0 auto 1rem',
        }} />
        <p style={{ color: '#64748b' }}>Verifying your email...</p>
      </div>
    </div>
  )
}

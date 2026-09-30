import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import api from '../lib/api'
import toast from 'react-hot-toast'

const forgotSchema = z.object({
  email: z.string().email('Invalid email address'),
})

export function ForgotPasswordPage() {
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [realMail, setRealMail] = useState(null)
  useEffect(() => {
    api.get('/auth/email-status').then(r => setRealMail(r.data.resend_configured)).catch(() => setRealMail(null))
  }, [])
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(forgotSchema),
  })

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await api.post('/auth/forgot-password', data)
      setSent(true)
    } catch {
      toast.error('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: '2rem 1.5rem',
      background: 'radial-gradient(ellipse at top, rgba(99,102,241,0.08) 0%, transparent 60%), #0f172a',
    }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 56, height: 56, borderRadius: '1rem',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem', margin: '0 auto 1rem',
          }}>🔑</div>
          <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Forgot password?</h1>
          <p style={{ color: '#64748b' }}>We'll send a reset link to your email.</p>
        </div>

        <div className="card" style={{ padding: '2rem' }}>
          {sent ? (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📬</div>
              <h3 style={{ marginBottom: '0.75rem' }}>Check your inbox</h3>
              <p style={{ color: '#64748b', marginBottom: '1rem' }}>
                If an account with that email exists, we've sent a reset link. It expires in 15 minutes.
              </p>
              {realMail === false && (
                <p style={{ color: '#f59e0b', fontSize: '0.8125rem', marginBottom: '1.5rem', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: '.5rem', padding: '.6rem .8rem' }}>
                  ⚠️ Real email is not configured on this server yet — check the backend console for the reset link (dev mode).
                </p>
              )}
              <Link to="/login" className="btn-ghost" style={{ display: 'inline-flex' }}>← Back to login</Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                  Email Address
                </label>
                <input
                  {...register('email')}
                  type="email"
                  className={`input ${errors.email ? 'error' : ''}`}
                  placeholder="you@example.com"
                />
                {errors.email && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.email.message}</p>}
              </div>
              <button type="submit" className="btn-primary" disabled={loading} style={{ justifyContent: 'center' }}>
                {loading ? (
                  <span className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', display: 'inline-block' }} />
                ) : '📧'} Send Reset Link
              </button>
              <Link to="/login" style={{ textAlign: 'center', color: '#64748b', fontSize: '0.875rem', textDecoration: 'none' }}>← Back to login</Link>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}


const resetSchema = z.object({
  new_password: z
    .string()
    .min(8, 'Minimum 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain a number'),
  confirm: z.string(),
}).refine(d => d.new_password === d.confirm, {
  message: 'Passwords do not match', path: ['confirm'],
})

export function ResetPasswordPage() {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const token = new URLSearchParams(window.location.search).get('token')

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(resetSchema),
  })

  const onSubmit = async (data) => {
    if (!token) return toast.error('Invalid reset link')
    setLoading(true)
    try {
      await api.post('/auth/reset-password', { token, new_password: data.new_password })
      setDone(true)
      toast.success('Password reset! Please log in.')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Reset failed or link expired')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: '2rem 1.5rem',
      background: 'radial-gradient(ellipse at top, rgba(99,102,241,0.08) 0%, transparent 60%), #0f172a',
    }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 56, height: 56, borderRadius: '1rem',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem', margin: '0 auto 1rem',
          }}>🔐</div>
          <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Reset Password</h1>
        </div>

        <div className="card" style={{ padding: '2rem' }}>
          {done ? (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
              <h3 style={{ marginBottom: '0.75rem' }}>Password Updated!</h3>
              <Link to="/login" className="btn-primary" style={{ display: 'inline-flex', justifyContent: 'center' }}>
                → Sign In Now
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>New Password</label>
                <input {...register('new_password')} type="password" className={`input ${errors.new_password ? 'error' : ''}`} placeholder="Min 8 chars, uppercase, number" />
                {errors.new_password && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.new_password.message}</p>}
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Confirm Password</label>
                <input {...register('confirm')} type="password" className={`input ${errors.confirm ? 'error' : ''}`} placeholder="Repeat your password" />
                {errors.confirm && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.confirm.message}</p>}
              </div>
              <button type="submit" className="btn-primary" disabled={loading} style={{ justifyContent: 'center' }}>
                {loading ? <span className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', display: 'inline-block' }} /> : '🔐'} Reset Password
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import GoogleButton from '../components/GoogleButton'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/dashboard'
  const [loading, setLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await login(data.email, data.password)
      toast.success('Welcome back! 👋')
      navigate(from, { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid email or password')
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
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 56, height: 56, borderRadius: '1rem',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem', margin: '0 auto 1rem',
          }}>⚡</div>
          <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Welcome back</h1>
          <p style={{ color: '#64748b', fontSize: '0.9375rem' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: '#a5b4fc', textDecoration: 'none', fontWeight: 600 }}>
              Sign up free
            </Link>
          </p>
        </div>

        <div className="card" style={{ padding: '2rem' }}>
          <GoogleButton />

          {import.meta.env.VITE_GOOGLE_CLIENT_ID && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '1rem',
              margin: '1.5rem 0', color: '#475569', fontSize: '0.8125rem',
            }}>
              <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.08)' }} />
              or continue with email
              <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.08)' }} />
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Email address
              </label>
              <input
                {...register('email')}
                type="email"
                className={`input ${errors.email ? 'error' : ''}`}
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.email && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.email.message}</p>}
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1' }}>Password</label>
                <Link to="/forgot-password" style={{ fontSize: '0.8125rem', color: '#6366f1', textDecoration: 'none' }}>
                  Forgot password?
                </Link>
              </div>
              <input
                {...register('password')}
                type="password"
                className={`input ${errors.password ? 'error' : ''}`}
                placeholder="Your password"
                autoComplete="current-password"
              />
              {errors.password && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.password.message}</p>}
            </div>

            <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '0.5rem', justifyContent: 'center' }}>
              {loading ? (
                <span className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', display: 'inline-block' }} />
              ) : '→'} Sign In
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

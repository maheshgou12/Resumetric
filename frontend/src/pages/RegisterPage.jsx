import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import GoogleButton from '../components/GoogleButton'

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Minimum 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  confirmPassword: z.string(),
}).refine((d) => d.password === d.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

const StrengthBar = ({ password }) => {
  const checks = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ]
  const strength = checks.filter(Boolean).length
  const colors = ['', '#ef4444', '#f59e0b', '#6366f1', '#10b981']
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong']

  if (!password) return null
  return (
    <div style={{ marginTop: '0.5rem' }}>
      <div style={{ display: 'flex', gap: 4, marginBottom: 4 }}>
        {[1, 2, 3, 4].map(i => (
          <div key={i} style={{
            flex: 1, height: 4, borderRadius: 2,
            background: i <= strength ? colors[strength] : 'rgba(255,255,255,0.08)',
            transition: 'background 0.3s',
          }} />
        ))}
      </div>
      <span style={{ fontSize: '0.75rem', color: colors[strength] }}>{labels[strength]}</span>
    </div>
  )
}

export default function RegisterPage() {
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [passwordValue, setPasswordValue] = useState('')

  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    resolver: zodResolver(schema),
  })

  const watchedPassword = watch('password', '')

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await registerUser(data.email, data.full_name, data.password)
      toast.success('Account created! Please verify your email. 🎉')
      navigate('/analyze')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
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
      <div style={{ width: '100%', maxWidth: 440 }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 56, height: 56, borderRadius: '1rem',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem', margin: '0 auto 1rem',
          }}>⚡</div>
          <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Create your account</h1>
          <p style={{ color: '#64748b', fontSize: '0.9375rem' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: '#a5b4fc', textDecoration: 'none', fontWeight: 600 }}>Sign in</Link>
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
              or register with email
              <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.08)' }} />
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Full Name
              </label>
              <input
                {...register('full_name')}
                className={`input ${errors.full_name ? 'error' : ''}`}
                placeholder="John Smith"
                autoComplete="name"
              />
              {errors.full_name && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.full_name.message}</p>}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Email Address
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
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Password
              </label>
              <input
                {...register('password')}
                type="password"
                className={`input ${errors.password ? 'error' : ''}`}
                placeholder="Min 8 chars, 1 uppercase, 1 number"
                autoComplete="new-password"
              />
              <StrengthBar password={watchedPassword} />
              {errors.password && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.password.message}</p>}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Confirm Password
              </label>
              <input
                {...register('confirmPassword')}
                type="password"
                className={`input ${errors.confirmPassword ? 'error' : ''}`}
                placeholder="Repeat your password"
                autoComplete="new-password"
              />
              {errors.confirmPassword && <p style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.confirmPassword.message}</p>}
            </div>

            <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '0.5rem', justifyContent: 'center' }}>
              {loading ? (
                <span className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', display: 'inline-block' }} />
              ) : '🚀'} Create Account
            </button>
          </form>

          <p style={{ color: '#475569', fontSize: '0.75rem', textAlign: 'center', marginTop: '1rem' }}>
            By signing up, you agree to our{' '}
            <Link to="/terms" style={{ color: '#a5b4fc', textDecoration: 'none' }}>Terms of Service</Link>
            {' '}and{' '}
            <Link to="/privacy" style={{ color: '#a5b4fc', textDecoration: 'none' }}>Privacy Policy</Link>.
          </p>
        </div>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_LINKS = [
  { href: '/analyze', label: 'Analyze' },
  { href: '/career', label: 'Score' },
  { href: '/resumes', label: 'Resumes' },
  { href: '/progress', label: 'Progress' },
  { href: '/roadmaps', label: 'Roadmaps' },
  { href: '/interview', label: 'Interview' },
  { href: '/dashboard', label: 'Dashboard' },
]

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const isActive = (href) => location.pathname === href

  return (
    <nav className="navbar">
      <div style={{
        maxWidth: 1200, margin: '0 auto', padding: '0 1.5rem',
        display: 'flex', alignItems: 'center', height: 64, gap: '1rem'
      }}>
        {/* Logo */}
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            width: 36, height: 36, borderRadius: '0.625rem',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1rem',
          }}>⚡</div>
          <span style={{
            fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.125rem',
            background: 'var(--gradient-brand)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
          }}>CareerLens AI</span>
        </Link>

        {/* Desktop nav */}
        <div style={{ flex: 1 }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          {user && NAV_LINKS.map(link => (
            <Link key={link.href} to={link.href} style={{
              textDecoration: 'none',
              padding: '0.5rem 0.875rem',
              borderRadius: '0.625rem',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: isActive(link.href) ? '#a5b4fc' : '#94a3b8',
              background: isActive(link.href) ? 'rgba(99,102,241,0.1)' : 'transparent',
              transition: 'all 0.15s',
            }}>
              {link.label}
            </Link>
          ))}
          {user && isAdmin && (
            <Link to="/admin" style={{
              textDecoration: 'none',
              padding: '0.5rem 0.875rem',
              borderRadius: '0.625rem',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: isActive('/admin') ? '#fbbf24' : '#94a3b8',
              background: isActive('/admin') ? 'rgba(251,191,36,0.1)' : 'transparent',
            }}>
              Admin
            </Link>
          )}
        </div>

        {/* Auth buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {!user ? (
            <>
              <Link to="/login" className="btn-ghost" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                Log in
              </Link>
              <Link to="/register" className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                Get Started
              </Link>
            </>
          ) : (
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                  background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
                  borderRadius: '2rem', padding: '0.375rem 0.75rem 0.375rem 0.375rem',
                  cursor: 'pointer', color: '#e2e8f0',
                }}
              >
                <div style={{
                  width: 28, height: 28, borderRadius: '50%',
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.75rem', fontWeight: 700, color: 'white', overflow: 'hidden',
                }}>
                  {user.avatar_url
                    ? <img src={user.avatar_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    : user.full_name?.[0]?.toUpperCase() || '?'
                  }
                </div>
                <span style={{ fontSize: '0.8125rem', fontWeight: 500, maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {user.full_name}
                </span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9l6 6 6-6"/>
                </svg>
              </button>

              {dropdownOpen && (
                <>
                  <div onClick={() => setDropdownOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 49 }} />
                  <div style={{
                    position: 'absolute', right: 0, top: 'calc(100% + 8px)',
                    background: '#1e293b', border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '0.875rem', padding: '0.5rem', minWidth: 200,
                    zIndex: 50, boxShadow: '0 16px 48px rgba(0,0,0,0.5)',
                    animation: 'fadeInUp 0.15s ease',
                  }}>
                    <div style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid rgba(255,255,255,0.06)', marginBottom: '0.25rem' }}>
                      <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#e2e8f0' }}>{user.full_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{user.email}</div>
                    </div>
                    {[
                      { href: '/analyze', icon: '⚡', label: 'New Analysis' },
                      { href: '/dashboard', icon: '📊', label: 'Dashboard' },
                    ].map(item => (
                      <Link key={item.href} to={item.href} onClick={() => setDropdownOpen(false)} style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem',
                        padding: '0.625rem 0.75rem', borderRadius: '0.5rem',
                        textDecoration: 'none', color: '#94a3b8', fontSize: '0.875rem',
                        transition: 'all 0.15s',
                      }}
                        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                      >
                        <span>{item.icon}</span> {item.label}
                      </Link>
                    ))}
                    <button onClick={handleLogout} style={{
                      display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%',
                      padding: '0.625rem 0.75rem', borderRadius: '0.5rem',
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: '#f87171', fontSize: '0.875rem', textAlign: 'left',
                      transition: 'all 0.15s',
                    }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(239,68,68,0.08)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                      <span>🚪</span> Log out
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}

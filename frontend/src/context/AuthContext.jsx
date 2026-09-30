import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setLoading(false)
        return
      }
      const resp = await api.get('/auth/me')
      setUser(resp.data)
    } catch {
      localStorage.removeItem('access_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMe()
  }, [fetchMe])

  const login = useCallback(async (email, password) => {
    const resp = await api.post('/auth/login', { email, password })
    localStorage.setItem('access_token', resp.data.access_token)
    setUser(resp.data.user)
    return resp.data.user
  }, [])

  const register = useCallback(async (email, full_name, password) => {
    const resp = await api.post('/auth/register', { email, full_name, password })
    localStorage.setItem('access_token', resp.data.access_token)
    setUser(resp.data.user)
    return resp.data.user
  }, [])

  const googleLogin = useCallback(async (idToken) => {
    const resp = await api.post('/auth/google', { id_token: idToken })
    localStorage.setItem('access_token', resp.data.access_token)
    setUser(resp.data.user)
    return resp.data.user
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout')
    } catch {}
    localStorage.removeItem('access_token')
    setUser(null)
  }, [])

  const updateUser = useCallback((updates) => {
    setUser((prev) => prev ? { ...prev, ...updates } : prev)
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      googleLogin,
      logout,
      updateUser,
      isAdmin: user?.role === 'admin',
      isAuthenticated: !!user,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

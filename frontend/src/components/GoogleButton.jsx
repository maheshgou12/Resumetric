import { useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function GoogleButton() {
  const { googleLogin } = useAuth()
  const navigate = useNavigate()

  const handleCredentialResponse = useCallback(async (response) => {
    try {
      await googleLogin(response.credential)
      toast.success('Signed in with Google! 🎉')
      navigate('/dashboard')
    } catch (err) {
      toast.error('Google sign-in failed')
    }
  }, [googleLogin, navigate])

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
    if (!clientId || !window.google) return

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleCredentialResponse,
    })
    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-btn'),
      {
        theme: 'outline',
        size: 'large',
        width: 400,
        text: 'continue_with',
        shape: 'rectangular',
      }
    )
  }, [handleCredentialResponse])

  // Google OAuth not configured (local mode) — hide the button entirely
  // instead of showing a dead button that only pops an error toast.
  if (!import.meta.env.VITE_GOOGLE_CLIENT_ID) {
    return null
  }

  return (
    <div>
      <div id="google-signin-btn" style={{ display: 'flex', justifyContent: 'center' }} />
    </div>
  )
}

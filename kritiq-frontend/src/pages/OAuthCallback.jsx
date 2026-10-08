import React, { useContext, useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext.jsx'
import axiosInstance from '../api/axiosInstance.js'
import LoadingState from '../components/LoadingState.jsx'

const ERROR_MESSAGES = {
  github_oauth_not_configured: 'GitHub OAuth is not configured on the server. Ask your administrator to set GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET and GITHUB_REDIRECT_URI.',
  github_access_denied: 'You denied access to your GitHub account. No changes were made.',
  github_invalid_state: 'OAuth state validation failed (possible CSRF). Please try logging in again.',
  github_missing_code: 'GitHub did not return an authorization code. Please try again.',
  github_invalid_code: 'The GitHub authorization code was invalid or already used. Please try again.',
  github_redirect_uri_mismatch: 'GitHub OAuth callback URL does not match the registered redirect URI. Update GITHUB_REDIRECT_URI or the GitHub App settings.',
  github_code_exchange_failed: 'Could not exchange the GitHub authorization code for a session. Please try again.',
  github_network_error: 'Network error while contacting GitHub. Please try again.',
  github_api_failed: 'GitHub user profile could not be loaded. Please try again.',
  github_oauth_error: 'GitHub sign-in failed. Please try again later.',
  account_linking_failed: 'Your GitHub account could not be linked to a Kritiq session. Please register manually.',
  missing_otc: 'No handoff code was returned from the OAuth callback. Please try again.',
  otc_invalid: 'The handoff code was expired, already used, or invalid. Please try again.',
  unknown: 'Sign-in failed for an unexpected reason. Please try again.',
}

export default function OAuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const auth = useContext(AuthContext)
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let cancelled = false

    async function run() {
      const errorCode = params.get('error')
      const otc = params.get('otc')
      const redirectTo = params.get('redirect') || '/dashboard'

      if (errorCode) {
        const msg = ERROR_MESSAGES[errorCode] || ERROR_MESSAGES.unknown
        if (!cancelled) {
          setErrorMessage(msg)
          setStatus('error')
        }
        return
      }

      if (!otc) {
        if (!cancelled) {
          setErrorMessage(ERROR_MESSAGES.missing_otc)
          setStatus('error')
        }
        return
      }

      try {
        const res = await axiosInstance.post('/auth/github/exchange', { code: otc })
        const payload = res?.data
        const token = payload?.access_token
        const tokenType = payload?.token_type
        if (!token || tokenType !== 'bearer') {
          throw new Error('bad_payload')
        }
        localStorage.setItem('token', token)
        if (auth?.setToken) auth.setToken(token)
        try {
          if (auth?.loginWithJwt) {
            await auth.loginWithJwt(token)
          } else if (auth?.loadSession) {
            await auth.loadSession()
          } else if (auth?.getProfile) {
            const user = await auth.getProfile()
            if (auth?.setUser) auth.setUser(user)
          }
        } catch (_profileErr) {
          if (!cancelled) {
            navigate(redirectTo, { replace: true })
          }
          return
        }
        if (!cancelled) {
          navigate(redirectTo, { replace: true })
        }
      } catch (err) {
        if (cancelled) return
        const detail = err?.response?.data?.detail
        let msg
        if (typeof detail === 'string' && /expired|already used|invalid/i.test(detail)) {
          msg = ERROR_MESSAGES.otc_invalid
        } else if (typeof detail === 'string') {
          msg = detail
        } else {
          msg = ERROR_MESSAGES.unknown
        }
        setErrorMessage(msg)
        setStatus('error')
      }
    }

    run()
    return () => {
      cancelled = true
    }
  }, [params, navigate, auth])

  return (
    <div className="bg-surface text-on-surface font-sans min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="max-w-md w-full px-sm">
        {status === 'loading' ? (
          <div className="flex flex-col items-center gap-md">
            <LoadingState message="Completing GitHub sign-in..." />
            <p className="font-body-sm text-on-surface-variant text-xs text-center">
              We're exchanging your GitHub identity for a Kritiq session.
            </p>
          </div>
        ) : (
          <div className="bg-surface-container rounded-lg border border-error-container p-md shadow-xl flex flex-col items-center gap-sm">
            <span className="material-symbols-outlined text-error text-[40px]">error</span>
            <h1 className="font-headline-sm text-error text-sm font-semibold">
              Sign-in failed
            </h1>
            <p className="font-body-sm text-on-surface-variant text-xs text-center leading-relaxed">
              {errorMessage}
            </p>
            <div className="flex gap-sm w-full mt-xs">
              <button
                onClick={() => navigate('/login', { replace: true })}
                className="flex-1 bg-surface-container-highest hover:bg-on-surface/5 text-on-surface font-label-lg px-sm py-xs rounded transition-colors"
              >
                Back to Login
              </button>
              <button
                onClick={() => navigate('/register', { replace: true })}
                className="flex-1 bg-primary hover:bg-on-primary-container text-on-primary font-label-lg px-sm py-xs rounded transition-colors"
              >
                Create Account
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

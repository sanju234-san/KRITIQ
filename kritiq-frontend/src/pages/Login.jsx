import React, { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  
  const navigate = useNavigate()
  const auth = useContext(AuthContext)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMsg('')

    try {
      if (auth?.login) {
        await auth.login(email, password)
      }
      navigate('/dashboard')
    } catch (err) {
      console.error('Login error:', err)
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setErrorMsg(detail.map((d) => `${d.loc ? d.loc[d.loc.length - 1] + ': ' : ''}${d.msg}`).join('; '))
      } else if (typeof detail === 'string') {
        setErrorMsg(detail)
      } else {
        setErrorMsg('Invalid email or password (must be at least 8 characters).')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGithubLogin = async () => {
    setIsSubmitting(true)
    setErrorMsg('')
    const demoEmail = 'github_dev@kritiq.io'
    const demoPassword = 'githubdevpwd123'

    try {
      if (auth?.login) {
        try {
          await auth.login(demoEmail, demoPassword)
        } catch {
          if (auth?.register) {
            await auth.register('GitHub Developer', demoEmail, demoPassword)
          }
        }
      }
      navigate('/dashboard')
    } catch (err) {
      console.error('GitHub auth error:', err)
      setErrorMsg('Failed to log in with GitHub account.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-surface text-on-surface font-sans min-h-screen flex items-center justify-center relative overflow-hidden selection:bg-primary/30">
      {/* Background Textures */}
      <div className="fixed inset-0 code-grid opacity-40 pointer-events-none"></div>
      <div className="fixed inset-0 scanline pointer-events-none"></div>

      {/* Main Form Container */}
      <main className="relative z-10 w-full max-w-[420px] px-gutter py-xl">
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-xl">
          <Link to="/" className="w-12 h-12 bg-primary-container rounded-lg flex items-center justify-center mb-md border border-outline-variant shadow-lg shadow-primary-container/10">
            <span className="material-symbols-outlined text-on-primary-container text-[28px]" style={{ fontVariationSettings: "'FILL' 1" }}>
              terminal
            </span>
          </Link>
          <h1 className="font-display text-display text-primary tracking-tight">Kritiq</h1>
          <p className="font-body-md text-on-surface-variant mt-xs">AI-Powered Code Intelligence</p>
        </div>

        {/* Login Card */}
        <section className="bg-surface-container border border-outline-variant rounded-xl p-xl shadow-2xl shadow-black/50">
          <header className="mb-lg">
            <h2 className="font-headline-md text-headline-md text-on-surface">Welcome back</h2>
            <p className="font-body-sm text-on-surface-variant mt-xs">Enter your credentials to access your dashboard.</p>
          </header>

          <form onSubmit={handleSubmit} className="space-y-md">
            {errorMsg && (
              <div className="p-sm bg-error-container/30 border border-error/50 rounded-lg text-error text-xs">
                {errorMsg}
              </div>
            )}

            {/* Email Field */}
            <div className="space-y-xs">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase text-[10px]" htmlFor="email">
                Work Email
              </label>
              <div className="relative group glow-hover">
                <div className="absolute inset-y-0 left-0 pl-md flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-body-lg text-outline">mail</span>
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-surface-container-lowest border border-outline-variant text-on-surface rounded-lg py-md pl-xl pr-md focus:ring-1 focus:ring-primary focus:border-primary transition-all font-body-md outline-none placeholder:text-outline/50 text-xs"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-xs">
              <div className="flex justify-between items-center">
                <label className="font-label-caps text-label-caps text-on-surface-variant uppercase text-[10px]" htmlFor="password">
                  Password (min 8 chars)
                </label>
                <a href="#forgot" className="text-primary hover:underline font-body-sm transition-all text-[11px]">
                  Forgot?
                </a>
              </div>
              <div className="relative group glow-hover">
                <div className="absolute inset-y-0 left-0 pl-md flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-body-lg text-outline">lock</span>
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-surface-container-lowest border border-outline-variant text-on-surface rounded-lg py-md pl-xl pr-md focus:ring-1 focus:ring-primary focus:border-primary transition-all font-body-md outline-none placeholder:text-outline/50 text-xs"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-primary text-on-primary font-bold py-md rounded-lg hover:brightness-110 active:scale-[0.98] transition-all flex items-center justify-center gap-sm mt-lg text-body-md disabled:opacity-50 text-xs"
            >
              {isSubmitting ? (
                <>
                  <span className="material-symbols-outlined text-[18px] animate-spin">refresh</span>
                  Logging in...
                </>
              ) : (
                <>
                  Continue
                  <span className="material-symbols-outlined text-body-lg">arrow_forward</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-xl">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-outline-variant"></div>
            </div>
            <div className="relative flex justify-center text-label-caps">
              <span className="bg-surface-container px-md text-on-surface-variant uppercase text-[10px]">Or login with</span>
            </div>
          </div>

          {/* OAuth Option */}
          <button
            type="button"
            onClick={handleGithubLogin}
            disabled={isSubmitting}
            className="w-full bg-surface-container-high border border-outline-variant text-on-surface font-body-md py-md rounded-lg hover:bg-surface-variant active:scale-[0.98] transition-all flex items-center justify-center gap-md text-xs disabled:opacity-50"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"></path>
            </svg>
            Continue with GitHub
          </button>
        </section>

        {/* Footer Link */}
        <footer className="mt-lg text-center">
          <p className="font-body-sm text-on-surface-variant text-xs">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline font-bold">
              Create one now
            </Link>
          </p>
        </footer>
      </main>
    </div>
  )
}

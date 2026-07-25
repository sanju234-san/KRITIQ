import React, { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

export default function Register() {
  const [name, setName] = useState('')
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
      if (auth?.register) {
        await auth.register(name, email, password)
      }
      navigate('/dashboard')
    } catch (err) {
      console.error('Register error:', err)
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setErrorMsg(detail.map((d) => `${d.loc ? d.loc[d.loc.length - 1] + ': ' : ''}${d.msg}`).join('; '))
      } else if (typeof detail === 'string') {
        setErrorMsg(detail)
      } else {
        setErrorMsg('Registration failed. Ensure password is at least 8 characters long.')
      }
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

        {/* Register Card */}
        <section className="bg-surface-container border border-outline-variant rounded-xl p-xl shadow-2xl shadow-black/50">
          <header className="mb-lg">
            <h2 className="font-headline-md text-headline-md text-on-surface">Create an Account</h2>
            <p className="font-body-sm text-on-surface-variant mt-xs">Start reviewing and translating code with context.</p>
          </header>

          <form onSubmit={handleSubmit} className="space-y-md">
            {errorMsg && (
              <div className="p-sm bg-error-container/30 border border-error/50 rounded-lg text-error text-xs">
                {errorMsg}
              </div>
            )}

            {/* Full Name Field */}
            <div className="space-y-xs">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase text-[10px]" htmlFor="name">
                Full Name
              </label>
              <div className="relative group glow-hover">
                <div className="absolute inset-y-0 left-0 pl-md flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-body-lg text-outline">person</span>
                </div>
                <input
                  id="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Alex Rivera"
                  className="w-full bg-surface-container-lowest border border-outline-variant text-on-surface rounded-lg py-md pl-xl pr-md focus:ring-1 focus:ring-primary focus:border-primary transition-all font-body-md outline-none placeholder:text-outline/50 text-xs"
                />
              </div>
            </div>

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
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase text-[10px]" htmlFor="password">
                Password (min 8 characters)
              </label>
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
                  Registering...
                </>
              ) : (
                <>
                  Create Account
                  <span className="material-symbols-outlined text-body-lg">arrow_forward</span>
                </>
              )}
            </button>
          </form>
        </section>

        {/* Footer Link */}
        <footer className="mt-lg text-center">
          <p className="font-body-sm text-on-surface-variant text-xs">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline font-bold">
              Log in here
            </Link>
          </p>
        </footer>
      </main>
    </div>
  )
}

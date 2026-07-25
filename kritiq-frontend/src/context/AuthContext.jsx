import React, { createContext, useState, useEffect } from 'react'
import { authApi } from '../api/authApi.js'

export const AuthContext = createContext(null)

/**
 * Validates that a JWT token has the correct structural format:
 * three base64url-encoded segments separated by dots, with a
 * JSON-parseable payload containing an 'exp' claim.
 * Does NOT verify the signature (that's the backend's job).
 */
function isValidTokenStructure(token) {
  if (!token || typeof token !== 'string') return false
  const parts = token.split('.')
  if (parts.length !== 3) return false
  try {
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    if (!payload || typeof payload !== 'object') return false
    if (typeof payload.exp !== 'number') return false
    // Reject obviously expired tokens (exp is Unix seconds)
    if (payload.exp * 1000 < Date.now()) {
      console.warn('Stored JWT has expired, clearing.')
      return false
    }
    return true
  } catch {
    return false
  }
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => {
    const stored = localStorage.getItem('token')
    if (stored && !isValidTokenStructure(stored)) {
      console.warn('Malformed or expired JWT found in localStorage, clearing.')
      localStorage.removeItem('token')
      return null
    }
    return stored
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken && isValidTokenStructure(storedToken)) {
        try {
          const profile = await authApi.getProfile()
          setUser(profile)
          setToken(storedToken)
        } catch (err) {
          console.error('Failed to load profile from stored token:', err)
          localStorage.removeItem('token')
          setToken(null)
          setUser(null)
        }
      } else if (storedToken) {
        // Token exists but is malformed — clear it
        localStorage.removeItem('token')
        setToken(null)
      }
      setLoading(false)
    }

    initAuth()
  }, [])

  const login = async (email, password) => {
    const data = await authApi.login(email, password)
    const access_token = data.access_token
    localStorage.setItem('token', access_token)
    setToken(access_token)
    
    try {
      const profile = await authApi.getProfile()
      setUser(profile)
    } catch {
      setUser({ email, name: 'Developer' })
    }
    return data
  }

  const register = async (name, email, password) => {
    const data = await authApi.register(name, email, password)
    const access_token = data.access_token
    localStorage.setItem('token', access_token)
    setToken(access_token)
    
    try {
      const profile = await authApi.getProfile()
      setUser(profile)
    } catch {
      setUser({ email, name })
    }
    return data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

import React, { createContext, useState, useEffect } from 'react'

// Dev domain - Auth state tracking
export const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      setUser({ email: 'user@example.com', name: 'Developer' })
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    setToken('mock-jwt-token')
    localStorage.setItem('token', 'mock-jwt-token')
    setUser({ email, name: 'Developer' })
    return true
  }

  const logout = () => {
    setToken(null)
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

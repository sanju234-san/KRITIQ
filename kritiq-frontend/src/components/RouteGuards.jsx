import React, { useContext, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import LoadingState from '../components/LoadingState'

export function ProtectedRoute({ children }) {
  const auth = useContext(AuthContext)
  const location = useLocation()

  if (auth?.loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <LoadingState message="Checking authentication..." />
      </div>
    )
  }

  if (!auth?.token || !auth?.user) {
    const redirect = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?redirect=${redirect}`} replace />
  }

  return children
}

export function GuestOnlyRoute({ children }) {
  const auth = useContext(AuthContext)
  const location = useLocation()
  const params = new URLSearchParams(location.search)
  const redirect = params.get('redirect') || '/dashboard'

  if (auth?.loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <LoadingState message="Loading..." />
      </div>
    )
  }

  if (auth?.token && auth?.user) {
    return <Navigate to={redirect} replace />
  }

  return children
}

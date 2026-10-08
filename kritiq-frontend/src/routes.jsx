import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import RepositoryConnect from './pages/RepositoryConnect.jsx'
import ReviewSubmit from './pages/ReviewSubmit.jsx'
import ReviewResult from './pages/ReviewResult.jsx'
import TranslationSubmit from './pages/TranslationSubmit.jsx'
import TranslationResult from './pages/TranslationResult.jsx'
import ExplanationResult from './pages/ExplanationResult.jsx'
import History from './pages/History.jsx'
import CliPublicDocs from './pages/CliPublicDocs.jsx'
import CliAppDocs from './pages/CliAppDocs.jsx'
import OAuthCallback from './pages/OAuthCallback.jsx'
import { ProtectedRoute, GuestOnlyRoute } from './components/RouteGuards.jsx'

const Protect = ({ children }) => <ProtectedRoute>{children}</ProtectedRoute>
const GuestOnly = ({ children }) => <GuestOnlyRoute>{children}</GuestOnlyRoute>

export const router = createBrowserRouter([
  { path: '/', element: <Landing /> },
  { path: '/cli', element: <CliPublicDocs /> },
  { path: '/cli-docs', element: <CliAppDocs /> },
  { path: '/auth/callback', element: <OAuthCallback /> },
  { path: '/login', element: <GuestOnly><Login /></GuestOnly> },
  { path: '/register', element: <GuestOnly><Register /></GuestOnly> },
  { path: '/dashboard', element: <Protect><Dashboard /></Protect> },
  { path: '/connect', element: <Protect><RepositoryConnect /></Protect> },
  { path: '/review', element: <Protect><ReviewSubmit /></Protect> },
  { path: '/review/:id', element: <Protect><ReviewResult /></Protect> },
  { path: '/translate', element: <Protect><TranslationSubmit /></Protect> },
  { path: '/translate/:id', element: <Protect><TranslationResult /></Protect> },
  { path: '/explanation/:id', element: <Protect><ExplanationResult /></Protect> },
  { path: '/history', element: <Protect><History /></Protect> }
])

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

export const router = createBrowserRouter([
  { path: '/', element: <Landing /> },
  { path: '/cli', element: <CliPublicDocs /> },
  { path: '/cli-docs', element: <CliAppDocs /> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '/dashboard', element: <Dashboard /> },
  { path: '/connect', element: <RepositoryConnect /> },
  { path: '/review', element: <ReviewSubmit /> },
  { path: '/review/:id', element: <ReviewResult /> },
  { path: '/translate', element: <TranslationSubmit /> },
  { path: '/translate/:id', element: <TranslationResult /> },
  { path: '/explanation/:id', element: <ExplanationResult /> },
  { path: '/history', element: <History /> }
])

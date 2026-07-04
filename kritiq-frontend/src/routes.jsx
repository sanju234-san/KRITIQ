import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import RepositoryConnect from './pages/RepositoryConnect.jsx'
import ReviewSubmit from './pages/ReviewSubmit.jsx'
import ReviewResult from './pages/ReviewResult.jsx'
import TranslationSubmit from './pages/TranslationSubmit.jsx'
import TranslationResult from './pages/TranslationResult.jsx'
import History from './pages/History.jsx'

// Dev domain - Route definition stub
export const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '/', element: <Dashboard /> },
  { path: '/connect', element: <RepositoryConnect /> },
  { path: '/review', element: <ReviewSubmit /> },
  { path: '/review/:id', element: <ReviewResult /> },
  { path: '/translate', element: <TranslationSubmit /> },
  { path: '/translate/:id', element: <TranslationResult /> },
  { path: '/history', element: <History /> }
])

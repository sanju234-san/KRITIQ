import React, { useContext } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

export default function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const auth = useContext(AuthContext)
  
  const user = auth?.user || { name: 'Alex Rivera', email: 'alex@example.com' }

  const mainNavItems = [
    { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { label: 'Repositories', path: '/connect', icon: 'folder_open' },
    { label: 'Reviews', path: '/review', icon: 'rate_review' },
    { label: 'Translations', path: '/translate', icon: 'translate' },
    { label: 'History', path: '/history', icon: 'history' },
  ]

  const resourceNavItems = [
    { label: 'Docs', path: '/cli-docs', icon: 'help' },
    { label: 'Settings', path: '/settings', icon: 'settings' },
  ]

  const handleLogout = () => {
    if (auth?.logout) {
      auth.logout()
    }
    navigate('/login')
  }

  return (
    <aside className="h-screen w-64 fixed left-0 top-0 border-r border-outline-variant bg-surface-container-low flex flex-col py-lg px-md z-50">
      {/* Brand Header */}
      <div className="mb-xl px-sm">
        <Link to="/" className="flex items-center gap-sm group">
          <div className="w-8 h-8 bg-primary-container rounded-lg flex items-center justify-center border border-outline-variant group-hover:scale-105 transition-transform">
            <span className="material-symbols-outlined text-on-primary-container text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>
              terminal
            </span>
          </div>
          <div>
            <h1 className="font-display text-headline-md text-primary tracking-tight leading-none">Kritiq</h1>
            <p className="font-body-sm text-on-surface-variant opacity-70 text-[10px] mt-0.5">AI Code Review</p>
          </div>
        </Link>
      </div>

      {/* Main Navigation Links */}
      <nav className="space-y-xs">
        {mainNavItems.map((item) => {
          const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path))
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-md px-md py-sm rounded-lg transition-colors duration-200 ${
                isActive
                  ? 'text-primary font-bold border-r-2 border-primary bg-surface-container-high'
                  : 'text-on-surface-variant font-medium hover:bg-surface-container-high hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="font-body-md">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Resources Section Header */}
      <div className="mt-lg pt-md border-t border-outline-variant/40">
        <p className="px-md font-label-caps text-[10px] uppercase text-on-surface-variant opacity-60 tracking-wider mb-xs">
          RESOURCES
        </p>
        <nav className="space-y-xs">
          {resourceNavItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-md px-md py-sm rounded-lg transition-colors duration-200 ${
                  isActive
                    ? 'text-primary font-bold border-r-2 border-primary bg-surface-container-high'
                    : 'text-on-surface-variant font-medium hover:bg-surface-container-high hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span className="font-body-md">{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Profile & Logout Box */}
      <div className="mt-auto border-t border-outline-variant pt-md flex items-center gap-sm px-xs">
        <div className="w-9 h-9 rounded-lg bg-surface-container-high border border-outline-variant flex items-center justify-center text-primary font-bold text-xs">
          {user.name ? user.name.charAt(0) : 'A'}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-body-md font-bold text-on-surface truncate text-xs">{user.name || 'Alex Rivera'}</p>
          <p className="font-body-sm text-on-surface-variant truncate text-[10px]">PREMIUM DEV</p>
        </div>
        <button
          onClick={handleLogout}
          title="Log out"
          className="p-xs text-on-surface-variant hover:text-error transition-colors rounded hover:bg-surface-container-high"
        >
          <span className="material-symbols-outlined text-[18px]">logout</span>
        </button>
      </div>
    </aside>
  )
}

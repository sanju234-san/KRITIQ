import React from 'react'
import { Link } from 'react-router-dom'

// Dev domain - Sidebar layout navigation stub
export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 border-r border-gray-700 text-slate-300 p-4">
      <div className="text-xl font-semibold text-white mb-6">Kritiq Panel</div>
      <nav className="space-y-2">
        <Link to="/" className="block p-2 hover:bg-gray-700 rounded">Dashboard</Link>
        <Link to="/connect" className="block p-2 hover:bg-gray-700 rounded">Repositories</Link>
        <Link to="/review" className="block p-2 hover:bg-gray-700 rounded">Code Review</Link>
        <Link to="/translate" className="block p-2 hover:bg-gray-700 rounded">Translation</Link>
        <Link to="/history" className="block p-2 hover:bg-gray-700 rounded">History</Link>
      </nav>
    </aside>
  )
}

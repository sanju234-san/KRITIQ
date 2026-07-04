import React, { useState } from 'react'
import NavBar from '../components/NavBar.jsx'
import Sidebar from '../components/Sidebar.jsx'
import IssueList from '../components/IssueList.jsx'

// Dev domain - Review Result page skeleton
export default function ReviewResult() {
  const [issues, setIssues] = useState([
    { id: 1, line: 12, severity: 'medium', message: 'Function lacks exception handling.' },
    { id: 2, line: 24, severity: 'low', message: 'Variables shadow built-ins.' }
  ])

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <NavBar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-900 p-6">
          <h1 className="text-3xl font-semibold text-slate-100 mb-6">Review Results</h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-lg bg-gray-800 p-6 shadow-md">
              <h2 className="text-xl font-bold text-white mb-4">Code View</h2>
              <div className="h-96 rounded bg-gray-900 p-4 font-mono text-sm text-slate-300 overflow-auto">
                {`def validate_user(user):
    # Medium Issue: Line 12
    db.save(user)
    return True`}
              </div>
            </div>

            <div className="rounded-lg bg-gray-800 p-6 shadow-md">
              <h2 className="text-xl font-bold text-white mb-4">Issues Found</h2>
              <IssueList issues={issues} />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

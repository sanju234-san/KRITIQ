import React from 'react'

// Dev domain - Issue list representation stub
export default function IssueList({ issues }) {
  return (
    <div className="space-y-2">
      {issues.map((issue) => (
        <div key={issue.id} className="p-3 bg-gray-900 border border-gray-700 rounded text-slate-300">
          <span className="font-bold text-red-500 capitalize">[{issue.severity}]</span> Line {issue.line}: {issue.message}
        </div>
      ))}
    </div>
  )
}

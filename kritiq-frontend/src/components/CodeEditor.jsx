import React from 'react'

// Dev domain - Monaco Editor wrapper stub
export default function CodeEditor({ code, onChange, language }) {
  return (
    <div className="bg-gray-900 text-white p-4 font-mono text-sm h-full">
      {/* TODO: Integrate @monaco-editor/react */}
      <textarea
        className="w-full h-full bg-transparent border-0 resize-none outline-none"
        value={code}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

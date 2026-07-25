import React from 'react'
import Editor from '@monaco-editor/react'

export default function CodeEditor({ code, onChange, language = 'python', readOnly = false, height = '100%' }) {
  const handleEditorChange = (value) => {
    if (onChange) {
      onChange(value || '')
    }
  }

  return (
    <div className="relative w-full h-full min-h-[300px] bg-[#1e1e1e] rounded-lg overflow-hidden border border-outline-variant">
      <Editor
        height={height}
        language={language.toLowerCase()}
        value={code || ''}
        theme="vs-dark"
        onChange={handleEditorChange}
        options={{
          readOnly: readOnly,
          minimap: { enabled: false },
          fontSize: 13,
          fontFamily: "'JetBrains Mono', monospace",
          lineHeight: 20,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          padding: { top: 12, bottom: 12 },
          lineNumbersMinChars: 3,
        }}
      />
    </div>
  )
}

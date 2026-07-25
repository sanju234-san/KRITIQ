import React from 'react'

export default function LoadingState({ message = 'Running context-aware AI analysis...' }) {
  return (
    <div className="flex flex-col items-center justify-center p-xl bg-surface-container rounded-xl border border-outline-variant text-center my-lg space-y-md">
      <div className="relative w-12 h-12 flex items-center justify-center">
        <div className="absolute inset-0 rounded-full border-2 border-primary/20 border-t-primary animate-spin"></div>
        <span className="material-symbols-outlined text-primary text-[24px]" style={{ fontVariationSettings: "'FILL' 1" }}>
          auto_awesome
        </span>
      </div>
      <div>
        <p className="font-headline-md text-body-md font-bold text-on-surface">{message}</p>
        <p className="font-mono text-code-sm text-on-surface-variant mt-xs">Inspecting AST &amp; RAG vector embeddings...</p>
      </div>
    </div>
  )
}

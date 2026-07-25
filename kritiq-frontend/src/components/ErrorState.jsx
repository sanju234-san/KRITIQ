import React from 'react'

export default function ErrorState({ error = 'Failed to execute context analysis.', onRetry }) {
  return (
    <div className="p-lg bg-error-container/20 rounded-xl border border-error/40 text-on-error-container my-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-md">
      <div className="flex items-start gap-md">
        <div className="p-xs bg-error-container rounded-lg text-on-error-container mt-0.5">
          <span className="material-symbols-outlined text-[24px]">warning</span>
        </div>
        <div>
          <h4 className="font-bold font-headline-md text-body-md text-error">Execution Error</h4>
          <p className="font-mono text-code-sm text-on-surface-variant mt-xs">{error}</p>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-error text-on-error px-md py-sm rounded-lg font-bold text-body-sm hover:brightness-110 transition-all flex items-center gap-xs"
        >
          <span className="material-symbols-outlined text-[16px]">refresh</span>
          Retry
        </button>
      )}
    </div>
  )
}

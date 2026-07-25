import React, { useState } from 'react'

export default function IssueList({ issues = [], onSelectLine }) {
  const [activeExplainId, setActiveExplainId] = useState(null)

  if (!issues || issues.length === 0) {
    return (
      <div className="p-lg bg-surface-container rounded-lg border border-outline-variant text-center">
        <span className="material-symbols-outlined text-tertiary text-[36px] mb-xs">check_circle</span>
        <p className="font-body-md text-on-surface font-bold">No Issues Found</p>
        <p className="font-body-sm text-on-surface-variant">The analyzed code passed all automated lint and logic checks.</p>
      </div>
    )
  }

  const getSeverityBadge = (severity = 'low') => {
    const sev = severity.toLowerCase()
    if (sev === 'high' || sev === 'critical') {
      return (
        <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-error-container text-on-error-container border border-error/30">
          High
        </span>
      )
    }
    if (sev === 'medium' || sev === 'warning') {
      return (
        <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-secondary-container text-on-secondary-container border border-secondary/30">
          Medium
        </span>
      )
    }
    return (
      <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-tertiary-container text-on-tertiary-container border border-tertiary/30">
        Low
      </span>
    )
  }

  return (
    <div className="space-y-md">
      {issues.map((issue, index) => {
        const issueTitle = issue.title || issue.message || `Issue #${index + 1}`
        const explanation = issue.explanation || 'No detailed explanation available.'
        const suggestedFix = issue.suggested_fix
        const line = issue.line || '—'
        const isExplaining = activeExplainId === index

        return (
          <div
            key={index}
            className="p-md bg-surface-container rounded-lg border border-outline-variant hover:border-primary transition-all group"
          >
            {/* Header / Badges */}
            <div className="flex items-center justify-between gap-sm mb-xs">
              <div className="flex items-center gap-xs">
                {getSeverityBadge(issue.severity)}
                <span className="font-mono text-code-sm text-on-surface-variant">Line {line}</span>
              </div>
              {onSelectLine && (
                <button
                  onClick={() => onSelectLine(line)}
                  className="text-[11px] font-body-sm text-primary hover:underline flex items-center gap-0.5"
                >
                  Jump to line
                  <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                </button>
              )}
            </div>

            {/* Title */}
            <h4 className="font-headline-md text-body-md font-bold text-on-surface mb-xs">{issueTitle}</h4>

            {/* Explanation */}
            <p className="font-body-sm text-on-surface-variant leading-relaxed mb-sm">{explanation}</p>

            {/* Suggested Fix */}
            {suggestedFix && (
              <div className="mt-sm p-sm bg-surface-container-lowest rounded border border-outline-variant font-mono text-code-sm">
                <p className="text-[10px] text-tertiary uppercase font-label-caps mb-xs flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">auto_fix_high</span>
                  Suggested Fix
                </p>
                <pre className="text-on-surface overflow-x-auto text-[11px] leading-relaxed whitespace-pre-wrap">
                  {suggestedFix}
                </pre>
              </div>
            )}

            {/* Action Bar */}
            <div className="mt-sm pt-xs border-t border-outline-variant/40 flex items-center justify-between">
              <button
                onClick={() => setActiveExplainId(isExplaining ? null : index)}
                className="text-[11px] font-body-sm text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-[14px]">psychology</span>
                {isExplaining ? 'Hide AI breakdown' : 'Explain in plain language'}
              </button>
            </div>

            {/* Expanded Plain Language Breakdown */}
            {isExplaining && (
              <div className="mt-xs p-sm bg-primary-container/10 border border-primary/30 rounded text-xs text-on-primary-container">
                <p className="font-bold flex items-center gap-1 mb-1 text-primary">
                  <span className="material-symbols-outlined text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                    auto_awesome
                  </span>
                  Plain Language Summary
                </p>
                <p className="leading-relaxed text-[11px]">
                  This issue occurs because the code does not safely validate inputs before execution. Refactoring this function ensures memory boundaries are respected and prevents unexpected execution bugs at runtime.
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

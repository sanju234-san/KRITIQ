import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const mdComponents = {
  code({ inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '')
    return !inline ? (
      <pre className="bg-surface-container-lowest border border-outline-variant rounded p-sm my-xs overflow-x-auto text-[11px] leading-relaxed">
        <code className={className} {...props}>
          {children}
        </code>
      </pre>
    ) : (
      <code className="bg-surface-container-lowest border border-outline-variant/60 rounded px-1 py-0.5 text-[11px] font-mono text-on-surface" {...props}>
        {children}
      </code>
    )
  },
  p({ children }) {
    return <p className="font-body-sm text-on-surface-variant leading-relaxed mb-sm">{children}</p>
  },
  ul({ children }) {
    return <ul className="list-disc list-inside pl-sm mb-sm space-y-0.5 text-on-surface-variant text-[12px]">{children}</ul>
  },
  ol({ children }) {
    return <ol className="list-decimal list-inside pl-sm mb-sm space-y-0.5 text-on-surface-variant text-[12px]">{children}</ol>
  },
  li({ children }) {
    return <li className="text-[12px]">{children}</li>
  },
  strong({ children }) {
    return <strong className="font-bold text-on-surface">{children}</strong>
  },
  a({ href, children }) {
    return <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:brightness-110">{children}</a>
  },
  blockquote({ children }) {
    return <blockquote className="border-l-2 border-outline-variant pl-sm my-sm text-on-surface-variant italic">{children}</blockquote>
  },
  h1({ children }) { return <h1 className="font-bold text-lg mb-sm text-on-surface">{children}</h1> },
  h2({ children }) { return <h2 className="font-bold text-[15px] mb-sm text-on-surface">{children}</h2> },
  h3({ children }) { return <h3 className="font-bold text-[13px] mb-sm text-on-surface">{children}</h3> },
  table({ children }) {
    return <table className="w-full border-collapse border border-outline-variant my-sm text-[11px]">{children}</table>
  },
  th({ children }) {
    return <th className="border border-outline-variant px-sm py-xs bg-surface-container-high text-on-surface font-bold">{children}</th>
  },
  td({ children }) {
    return <td className="border border-outline-variant px-sm py-xs text-on-surface-variant">{children}</td>
  },
}

const mdComponentsFix = {
  ...mdComponents,
  p({ children }) {
    return <p className="text-on-surface leading-relaxed mb-xs">{children}</p>
  },
}

function cleanIssueTitle(value, index) {
  let title = String(value || '').trim()
  const boldMatch = title.match(/^\*\*(.+?)\*\*/s)
  if (boldMatch) title = boldMatch[1].trim()
  title = title.replace(/\*{1,3}/g, '').replace(/_{1,3}/g, '').replace(/`/g, '')
  title = title.replace(/\s*\*{0,3}Line\s*:?\s*\d+.*$/i, '').trim()
  title = title.replace(/\s+-\s*$/, '').trim()
  return title || `Issue #${index + 1}`
}

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
        const issueTitle = cleanIssueTitle(issue.title || issue.message, index)
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
            <div className="mb-sm ai-md">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                {explanation}
              </ReactMarkdown>
            </div>

            {/* Suggested Fix */}
            {suggestedFix && (
              <div className="mt-sm p-sm bg-surface-container-lowest rounded border border-outline-variant">
                <p className="text-[10px] text-tertiary uppercase font-label-caps mb-xs flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">auto_fix_high</span>
                  Suggested Fix
                </p>
                <div className="ai-md-fix">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponentsFix}>
                    {suggestedFix}
                  </ReactMarkdown>
                </div>
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

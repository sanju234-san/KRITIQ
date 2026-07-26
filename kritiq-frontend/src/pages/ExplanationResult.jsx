import React, { useState, useEffect } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import CodeEditor from '../components/CodeEditor'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import { explanationApi } from '../api/explanationApi.js'

export default function ExplanationResult() {
  const { id } = useParams()
  const location = useLocation()

  const [explanationData, setExplanationData] = useState(location.state?.initialResult || null)
  const [code, setCode] = useState(location.state?.code || '# Explained code snippet')
  const [language, setLanguage] = useState(location.state?.language || 'python')
  const [filename, setFilename] = useState(location.state?.filename || 'snippet.py')

  const [loading, setLoading] = useState(!location.state?.initialResult)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!location.state?.initialResult && id) {
      const fetchExplanation = async () => {
        setLoading(true)
        setError(null)
        try {
          const data = await explanationApi.getExplanationResult(id)
          setExplanationData(data)
          if (data?.code) setCode(data.code)
          if (data?.language) setLanguage(data.language)
          if (data?.filename) setFilename(data.filename)
        } catch (err) {
          console.error('Failed to load explanation result:', err)
          const detail = err?.response?.data?.detail
          setError(detail || 'Explanation record not found or inaccessible.')
        } finally {
          setLoading(false)
        }
      }

      fetchExplanation()
    }
  }, [id, location.state])

  const explanationText = explanationData?.explanation || 'No explanation generated yet.'
  const createdAt = explanationData?.created_at || null

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <NavBar
          title={`Code Explanation #${id ? id.substring(0, 8) : 'Result'}`}
          actionButton={
            <Link
              to="/dashboard"
              className="bg-surface-container-high text-on-surface border border-outline-variant px-md py-2 rounded-lg font-bold text-body-sm hover:bg-surface-variant transition-all flex items-center gap-xs text-xs"
            >
              <span className="material-symbols-outlined text-[18px]">replay</span>
              Back to Dashboard
            </Link>
          }
        />

        <main className="mt-16 flex-1 grid lg:grid-cols-2 gap-md p-md overflow-hidden">
          {/* Left Column: Monaco Code Viewer */}
          <div className="flex flex-col h-full overflow-hidden bg-surface-container rounded-xl border border-outline-variant">
            <div className="px-md py-sm bg-surface-container-high border-b border-outline-variant flex justify-between items-center">
              <span className="font-mono text-code-sm text-on-surface font-bold">
                {filename}
              </span>
              <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-tertiary-container/20 text-tertiary border border-tertiary/30">
                {language}
              </span>
            </div>
            <div className="flex-1 min-h-0">
              <CodeEditor
                code={code}
                language={language}
                readOnly={true}
                height="100%"
              />
            </div>
          </div>

          {/* Right Column: AI Explanation */}
          <div className="flex flex-col h-full overflow-y-auto space-y-md pr-xs hide-scrollbar">
            {loading ? (
              <LoadingState message="Fetching stored explanation from database..." />
            ) : error ? (
              <ErrorState error={error} />
            ) : (
              <>
                {/* Meta Info */}
                {createdAt && (
                  <div className="p-sm bg-surface-container-lowest border border-outline-variant rounded-lg text-[11px] text-on-surface-variant font-mono flex items-center gap-xs">
                    <span className="material-symbols-outlined text-[16px]">schedule</span>
                    Generated: {new Date(createdAt).toLocaleString()}
                  </div>
                )}

                {/* Explanation Card */}
                <div className="p-md bg-surface-container rounded-xl border border-outline-variant space-y-xs">
                  <div className="flex items-center gap-1 text-tertiary font-bold text-body-sm font-sans">
                    <span className="material-symbols-outlined text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                      auto_awesome
                    </span>
                    Plain-Language Explanation
                  </div>
                  <div className="font-body-sm text-on-surface leading-relaxed text-sm whitespace-pre-wrap break-words">
                    {explanationText}
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="p-md bg-surface-container rounded-xl border border-outline-variant flex flex-wrap gap-xs">
                  <Link
                    to="/review"
                    className="bg-primary/10 text-primary hover:bg-primary/20 border border-primary/30 px-md py-xs rounded-lg font-bold text-xs transition-colors flex items-center gap-xs"
                  >
                    <span className="material-symbols-outlined text-[16px]">rate_review</span>
                    Review This Code
                  </Link>
                  <Link
                    to="/translate"
                    className="bg-secondary/10 text-secondary hover:bg-secondary/20 border border-secondary/30 px-md py-xs rounded-lg font-bold text-xs transition-colors flex items-center gap-xs"
                  >
                    <span className="material-symbols-outlined text-[16px]">translate</span>
                    Translate This Code
                  </Link>
                  <Link
                    to="/history"
                    className="bg-surface-container-high text-on-surface-variant hover:text-on-surface border border-outline-variant px-md py-xs rounded-lg font-bold text-xs transition-colors flex items-center gap-xs"
                  >
                    <span className="material-symbols-outlined text-[16px]">history</span>
                    View History
                  </Link>
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

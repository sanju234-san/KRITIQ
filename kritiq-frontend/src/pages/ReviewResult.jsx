import React, { useState, useEffect } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import CodeEditor from '../components/CodeEditor'
import IssueList from '../components/IssueList'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import { reviewApi } from '../api/reviewApi.js'

export default function ReviewResult() {
  const { id } = useParams()
  const location = useLocation()
  const [activeTab, setActiveTab] = useState('issues')

  const [reviewData, setReviewData] = useState(location.state?.initialResult || null)
  const [code, setCode] = useState(location.state?.code || '# Analyzed code snippet')
  const [language, setLanguage] = useState(location.state?.language || 'python')
  const [filename, setFilename] = useState(location.state?.filename || 'snippet.py')

  const [loading, setLoading] = useState(!location.state?.initialResult)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!location.state?.initialResult && id) {
      const fetchReview = async () => {
        setLoading(true)
        setError(null)
        try {
          const data = await reviewApi.getReviewResult(id)
          setReviewData(data)
          if (data?.code) setCode(data.code)
          if (data?.language) setLanguage(data.language)
          if (data?.filename) setFilename(data.filename)
        } catch (err) {
          console.error('Failed to load review result:', err)
          setError(err?.response?.data?.detail || 'Review record not found or inaccessible.')
        } finally {
          setLoading(false)
        }
      }

      fetchReview()
    }
  }, [id, location.state])

  const summary = reviewData?.summary || 'No review summary generated.'
  const issues = reviewData?.issues || []
  const rawOutput = reviewData?.raw_output || ''

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <NavBar
          title={`Review Results #${id ? id.substring(0, 8) : 'Result'}`}
          actionButton={
            <Link
              to="/review"
              className="bg-surface-container-high text-on-surface border border-outline-variant px-md py-2 rounded-lg font-bold text-body-sm hover:bg-surface-variant transition-all flex items-center gap-xs text-xs"
            >
              <span className="material-symbols-outlined text-[18px]">replay</span>
              New Analysis
            </Link>
          }
        />

        <main className="mt-16 flex-1 grid lg:grid-cols-2 gap-md p-md overflow-hidden">
          {/* Left Column: Monaco Code Viewer */}
          <div className="flex flex-col h-full overflow-hidden bg-surface-container rounded-xl border border-outline-variant">
            <div className="px-md py-sm bg-surface-container-high border-b border-outline-variant flex justify-between items-center">
              <span className="font-mono text-code-sm text-on-surface font-bold">{filename}</span>
              <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-primary-container/20 text-primary border border-primary/30">
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

          {/* Right Column: AI Review Summary & Flagged Issues */}
          <div className="flex flex-col h-full overflow-y-auto space-y-md pr-xs hide-scrollbar">
            {loading ? (
              <LoadingState message="Fetching review analysis from database..." />
            ) : error ? (
              <ErrorState error={error} />
            ) : (
              <>
                {/* Summary Box */}
                <div className="p-md bg-surface-container rounded-xl border border-outline-variant space-y-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-primary font-bold text-body-sm flex items-center gap-1 font-sans">
                      <span className="material-symbols-outlined text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                        auto_awesome
                      </span>
                      AI Review Summary
                    </span>
                    <span className="text-on-surface-variant text-[11px]">
                      Issues: {issues.length}
                    </span>
                  </div>
                  <p className="font-body-sm text-on-surface leading-relaxed text-xs">
                    {summary}
                  </p>
                </div>

                {/* Tabs Bar */}
                <div className="flex border-b border-outline-variant">
                  <button
                    onClick={() => setActiveTab('issues')}
                    className={`px-md py-sm font-bold text-body-sm border-b-2 transition-colors ${
                      activeTab === 'issues' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Flagged Issues ({issues.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('raw')}
                    className={`px-md py-sm font-bold text-body-sm border-b-2 transition-colors ${
                      activeTab === 'raw' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Raw AI Output
                  </button>
                </div>

                {/* Tab Contents */}
                {activeTab === 'issues' ? (
                  <IssueList issues={issues} />
                ) : (
                  <div className="p-md bg-surface-container-lowest border border-outline-variant rounded-lg font-mono text-code-sm overflow-x-auto text-[11px] whitespace-pre-wrap leading-relaxed text-on-surface">
                    {rawOutput || 'No raw output string available.'}
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

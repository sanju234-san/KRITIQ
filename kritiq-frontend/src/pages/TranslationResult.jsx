import React, { useState, useEffect } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import CodeEditor from '../components/CodeEditor'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import { translationApi } from '../api/translationApi.js'

export default function TranslationResult() {
  const { id } = useParams()
  const location = useLocation()

  const [translationData, setTranslationData] = useState(location.state?.initialResult || null)
  const [sourceCode] = useState(location.state?.sourceCode || '# Source snippet')
  const [sourceLang] = useState(location.state?.sourceLang || 'python')
  const [targetLang] = useState(location.state?.targetLang || 'java')

  const [loading, setLoading] = useState(!location.state?.initialResult)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!location.state?.initialResult && id) {
      const fetchTranslation = async () => {
        setLoading(true)
        setError(null)
        try {
          const data = await translationApi.getTranslationResult(id)
          setTranslationData(data)
        } catch (err) {
          console.error('Failed to load translation result:', err)
          setError(err?.response?.data?.detail || 'Translation record not found or inaccessible.')
        } finally {
          setLoading(false)
        }
      }

      fetchTranslation()
    }
  }, [id, location.state])

  const translatedCode = translationData?.translated_code || '// No translated code available.'
  const notes = translationData?.notes || 'Translation process completed successfully.'

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <NavBar
          title={`Translation Output #${id ? id.substring(0, 8) : 'Output'}`}
          actionButton={
            <Link
              to="/translate"
              className="bg-surface-container-high text-on-surface border border-outline-variant px-md py-2 rounded-lg font-bold text-body-sm hover:bg-surface-variant transition-all flex items-center gap-xs text-xs"
            >
              <span className="material-symbols-outlined text-[18px]">replay</span>
              New Translation
            </Link>
          }
        />

        <main className="mt-16 flex-1 flex flex-col p-md space-y-md overflow-hidden">
          {loading ? (
            <LoadingState message="Fetching translation result from database..." />
          ) : error ? (
            <ErrorState error={error} />
          ) : (
            <>
              {/* Side-by-side Monaco Editors Container */}
              <div className="flex-1 grid lg:grid-cols-2 gap-md min-h-0">
                {/* Left: Original Source Code */}
                <div className="flex flex-col h-full overflow-hidden bg-surface-container rounded-xl border border-outline-variant">
                  <div className="px-md py-sm bg-surface-container-high border-b border-outline-variant flex justify-between items-center">
                    <span className="font-mono text-code-sm text-on-surface font-bold">Source ({sourceLang})</span>
                    <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-surface-container-lowest text-on-surface-variant">
                      Original
                    </span>
                  </div>
                  <div className="flex-1 min-h-0">
                    <CodeEditor
                      code={sourceCode}
                      language={sourceLang}
                      readOnly={true}
                      height="100%"
                    />
                  </div>
                </div>

                {/* Right: Translated Target Code */}
                <div className="flex flex-col h-full overflow-hidden bg-surface-container rounded-xl border border-outline-variant">
                  <div className="px-md py-sm bg-surface-container-high border-b border-outline-variant flex justify-between items-center">
                    <span className="font-mono text-code-sm text-secondary font-bold">Target ({targetLang})</span>
                    <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-secondary-container text-on-secondary-container">
                      Translated by KRITIQ AI
                    </span>
                  </div>
                  <div className="flex-1 min-h-0">
                    <CodeEditor
                      code={translatedCode}
                      language={targetLang}
                      readOnly={true}
                      height="100%"
                    />
                  </div>
                </div>
              </div>

              {/* Bottom Translation Notes */}
              <div className="p-md bg-surface-container rounded-xl border border-outline-variant space-y-xs flex-shrink-0">
                <div className="flex items-center gap-sm text-secondary font-bold text-body-sm font-sans">
                  <span className="material-symbols-outlined text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                    auto_awesome
                  </span>
                  Translation Notes &amp; Insights
                </div>
                <p className="font-body-sm text-on-surface-variant leading-relaxed text-xs font-mono">
                  {notes}
                </p>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

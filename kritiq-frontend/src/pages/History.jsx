import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import { historyApi } from '../api/historyApi.js'

export default function History() {
  const [filter, setFilter] = useState('all')
  const [historyItems, setHistoryItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHistory = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await historyApi.getHistory()
      setHistoryItems(data?.history || [])
    } catch (err) {
      console.error('Failed to load history:', err)
      let detail = err?.response?.data?.detail
      if (err?.response?.status === 401 || detail === 'Not authenticated') {
        detail = 'Please Log In or Register to view your activity history.'
      }
      setError(detail || 'Failed to retrieve activity history.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const filteredItems = historyItems.filter((item) => {
    if (filter === 'review') return item.type === 'review'
    if (filter === 'translation') return item.type === 'translation'
    if (filter === 'explanation') return item.type === 'explanation'
    return true
  })

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64">
        <NavBar title="Activity History" />

        <main className="mt-16 p-lg space-y-lg max-w-6xl mx-auto">
          {/* Header & Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-md">
            <div>
              <h2 className="font-headline-lg text-headline-lg text-on-surface">Analysis &amp; Translation Logs</h2>
              <p className="font-body-md text-on-surface-variant mt-xs text-xs">
                Timestamped audit log of all automated AI code reviews and cross-language translations.
              </p>
            </div>

            {/* Filter Buttons */}
            <div className="flex items-center gap-xs bg-surface-container border border-outline-variant p-1 rounded-lg">
              <button
                onClick={() => setFilter('all')}
                className={`px-md py-xs rounded text-xs font-bold transition-colors ${
                  filter === 'all' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                All Logs
              </button>
              <button
                onClick={() => setFilter('review')}
                className={`px-md py-xs rounded text-xs font-bold transition-colors ${
                  filter === 'review' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                Reviews
              </button>
              <button
                onClick={() => setFilter('translation')}
                className={`px-md py-xs rounded text-xs font-bold transition-colors ${
                  filter === 'translation' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                Translations
              </button>
              <button
                onClick={() => setFilter('explanation')}
                className={`px-md py-xs rounded text-xs font-bold transition-colors ${
                  filter === 'explanation' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                Explanations
              </button>
            </div>
          </div>

          {/* History List Table */}
          {loading ? (
            <LoadingState message="Loading activity history from database..." />
          ) : error ? (
            <div className="p-lg bg-surface-container rounded-xl border border-outline-variant text-center space-y-md">
              <ErrorState error={error} onRetry={fetchHistory} />
              {error.includes('Log In') && (
                <div className="pt-2">
                  <Link
                    to="/login"
                    className="bg-primary text-on-primary px-lg py-sm rounded-lg font-bold text-xs hover:brightness-110"
                  >
                    Go to Log In
                  </Link>
                </div>
              )}
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="p-xl bg-surface-container border border-outline-variant rounded-xl text-center text-on-surface-variant text-xs">
              No activity logs recorded yet for this filter.
            </div>
          ) : (
            <div className="bg-surface-container border border-outline-variant rounded-xl overflow-hidden divide-y divide-outline-variant/40 shadow-lg">
              {filteredItems.map((item) => {
                const targetLink = item.type === 'review'
                  ? (item.details?.review_id ? `/review/${item.details.review_id}` : '/review')
                  : item.type === 'translation'
                  ? (item.details?.translation_id ? `/translate/${item.details.translation_id}` : '/translate')
                  : item.type === 'explanation'
                  ? (item.details?.explanation_id ? `/explanation/${item.details.explanation_id}` : '/dashboard')
                  : '/dashboard'

                const detailsText = item.details?.filename 
                  ? `File: ${item.details.filename}` 
                  : item.details?.source_language && item.details?.target_language
                  ? `Stack: ${item.details.source_language} → ${item.details.target_language}`
                  : item.details?.language
                  ? `Language: ${item.details.language}`
                  : 'Activity log entry'

                return (
                  <div
                    key={item.id}
                    className="p-md flex flex-col sm:flex-row sm:items-center justify-between gap-md hover:bg-surface-container-high transition-colors"
                  >
                    <div className="flex items-center gap-md">
                      <div className="w-10 h-10 rounded-lg bg-surface-container-high border border-outline-variant flex items-center justify-center text-primary flex-shrink-0">
                        <span className="material-symbols-outlined text-[22px]">
                          {item.type === 'review' ? 'rate_review' : item.type === 'translation' ? 'translate' : item.type === 'explanation' ? 'psychology' : 'history'}
                        </span>
                      </div>
                      <div>
                        <div className="flex items-center gap-sm">
                          <h4 className="font-headline-md text-body-md font-bold text-on-surface text-xs">{item.summary}</h4>
                          <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-tertiary-container text-on-tertiary-container">
                            {item.type}
                          </span>
                        </div>
                        <p className="font-body-sm text-on-surface-variant text-xs mt-0.5">{detailsText}</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between sm:justify-end gap-lg">
                      <div className="text-left sm:text-right font-mono text-code-sm text-on-surface-variant text-[11px]">
                        <p className="text-on-surface font-semibold text-[11px]">
                          {item.timestamp ? new Date(item.timestamp).toLocaleDateString() : 'Log'}
                        </p>
                        <p className="text-[10px] text-outline">
                          {item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        </p>
                      </div>

                      <Link
                        to={targetLink}
                        className="border border-outline-variant text-primary hover:bg-primary-container/10 px-md py-xs rounded-lg font-bold text-xs transition-colors flex items-center gap-1 whitespace-nowrap"
                      >
                        Revisit
                        <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                      </Link>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

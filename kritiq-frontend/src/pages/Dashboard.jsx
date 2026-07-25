import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import { historyApi } from '../api/historyApi.js'
import { repositoryApi } from '../api/repositoryApi.js'

export default function Dashboard() {
  const [historyItems, setHistoryItems] = useState([])
  const [repos, setRepos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [histRes, reposRes] = await Promise.all([
          historyApi.getHistory().catch(() => ({ history: [] })),
          repositoryApi.getRepos().catch(() => [])
        ])
        setHistoryItems(histRes?.history || [])
        setRepos(reposRes || [])
      } catch (err) {
        console.error('Failed to load dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  const reviewCount = historyItems.filter((i) => i.type === 'review').length
  const translationCount = historyItems.filter((i) => i.type === 'translation').length

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64">
        <NavBar
          actionButton={
            <Link
              to="/review"
              className="bg-primary-container text-on-primary-container px-md py-2 rounded-lg font-bold text-body-sm hover:brightness-110 transition-all flex items-center gap-xs"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Review
            </Link>
          }
        />

        <main className="mt-16 p-lg space-y-lg max-w-7xl mx-auto">
          {/* Hero Banner CTA */}
          <section className="relative overflow-hidden rounded-xl border border-outline-variant bg-surface-container p-xl flex flex-col md:flex-row justify-between items-center gap-lg shadow-sm">
            <div className="relative z-10 space-y-xs max-w-xl">
              <h2 className="font-headline-lg text-headline-lg text-on-surface">Accelerate your code reviews</h2>
              <p className="font-body-lg text-on-surface-variant text-sm">
                Connect your GitHub repositories to get context-aware AI analysis, vulnerability detection, and cross-language translations.
              </p>
              <div className="pt-sm">
                <Link
                  to="/connect"
                  className="bg-primary-container text-on-primary-container px-lg py-sm rounded-lg font-bold inline-flex items-center gap-sm hover:brightness-110 transition-all text-xs"
                >
                  <span className="material-symbols-outlined text-[18px]">add_link</span>
                  Connect GitHub Repo
                </Link>
              </div>
            </div>
            <div className="w-44 h-28 bg-surface-container-high rounded-lg border border-outline-variant p-md flex flex-col justify-center items-center text-center">
              <span className="material-symbols-outlined text-primary text-[32px] mb-xs" style={{ fontVariationSettings: "'FILL' 1" }}>
                auto_awesome
              </span>
              <span className="font-mono text-code-sm text-on-surface font-bold">MCP Vector Index</span>
              <span className="text-[10px] text-tertiary">Active &amp; Synced</span>
            </div>
          </section>

          {/* Metrics Grid */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-md">
            <div className="p-md bg-surface-container border border-outline-variant rounded-xl">
              <p className="font-label-caps text-on-surface-variant uppercase text-[10px]">Total Reviews</p>
              <h3 className="font-display text-display text-primary mt-xs">{loading ? '...' : reviewCount}</h3>
              <p className="font-body-sm text-tertiary text-[11px] mt-xs flex items-center gap-0.5">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> Live from DB
              </p>
            </div>

            <div className="p-md bg-surface-container border border-outline-variant rounded-xl">
              <p className="font-label-caps text-on-surface-variant uppercase text-[10px]">Translations</p>
              <h3 className="font-display text-display text-secondary mt-xs">{loading ? '...' : translationCount}</h3>
              <p className="font-body-sm text-on-surface-variant text-[11px] mt-xs">Multi-language</p>
            </div>

            <div className="p-md bg-surface-container border border-outline-variant rounded-xl">
              <p className="font-label-caps text-on-surface-variant uppercase text-[10px]">Connected Repos</p>
              <h3 className="font-display text-display text-tertiary mt-xs">{loading ? '...' : repos.length}</h3>
              <p className="font-body-sm text-tertiary text-[11px] mt-xs">GitHub REST Verified</p>
            </div>

            <div className="p-md bg-surface-container border border-outline-variant rounded-xl">
              <p className="font-label-caps text-on-surface-variant uppercase text-[10px]">Code Health Score</p>
              <h3 className="font-display text-display text-on-surface mt-xs">94%</h3>
              <p className="font-body-sm text-tertiary text-[11px] mt-xs">Passing threshold</p>
            </div>
          </section>

          {/* Quick Actions & Recent Activity */}
          <div className="grid lg:grid-cols-3 gap-lg">
            {/* Quick Actions */}
            <div className="space-y-md">
              <h3 className="font-headline-md text-body-md font-bold text-on-surface">Quick Actions</h3>
              
              <Link
                to="/review"
                className="block p-md bg-surface-container border border-outline-variant rounded-xl hover:border-primary transition-all group"
              >
                <div className="flex items-center gap-md">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:scale-105 transition-transform">
                    <span className="material-symbols-outlined">rate_review</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-body-md text-on-surface">Start Code Review</h4>
                    <p className="font-body-sm text-on-surface-variant text-xs">Paste code or select file from connected repo</p>
                  </div>
                </div>
              </Link>

              <Link
                to="/translate"
                className="block p-md bg-surface-container border border-outline-variant rounded-xl hover:border-primary transition-all group"
              >
                <div className="flex items-center gap-md">
                  <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary group-hover:scale-105 transition-transform">
                    <span className="material-symbols-outlined">translate</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-body-md text-on-surface">Cross-Language Translate</h4>
                    <p className="font-body-sm text-on-surface-variant text-xs">Port logic between Python, Java, C++, Go</p>
                  </div>
                </div>
              </Link>

              <Link
                to="/connect"
                className="block p-md bg-surface-container border border-outline-variant rounded-xl hover:border-primary transition-all group"
              >
                <div className="flex items-center gap-md">
                  <div className="w-10 h-10 rounded-lg bg-tertiary/10 flex items-center justify-center text-tertiary group-hover:scale-105 transition-transform">
                    <span className="material-symbols-outlined">link</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-body-md text-on-surface">Connect Repositories</h4>
                    <p className="font-body-sm text-on-surface-variant text-xs">Link GitHub repositories for MCP scanning</p>
                  </div>
                </div>
              </Link>
            </div>

            {/* Recent Activity List */}
            <div className="lg:col-span-2 space-y-md">
              <div className="flex justify-between items-center">
                <h3 className="font-headline-md text-body-md font-bold text-on-surface">Recent Activity</h3>
                <Link to="/history" className="text-xs text-primary hover:underline font-body-sm">
                  View all history
                </Link>
              </div>

              <div className="bg-surface-container border border-outline-variant rounded-xl overflow-hidden divide-y divide-outline-variant/40">
                {loading ? (
                  <div className="p-md text-center text-on-surface-variant text-xs font-mono">Loading activity feed...</div>
                ) : historyItems.length === 0 ? (
                  <div className="p-md text-center text-on-surface-variant text-xs">No recent activity yet. Submit a review or connect a repo to get started!</div>
                ) : (
                  historyItems.slice(0, 5).map((act) => {
                    const link = act.type === 'review' 
                      ? (act.details?.review_id ? `/review/${act.details.review_id}` : '/history')
                      : act.type === 'translation'
                      ? (act.details?.translation_id ? `/translate/${act.details.translation_id}` : '/history')
                      : '/history'

                    return (
                      <Link
                        key={act.id}
                        to={link}
                        className="p-md flex items-center justify-between hover:bg-surface-container-high transition-colors block"
                      >
                        <div className="flex items-center gap-md">
                          <div className="w-8 h-8 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
                            <span className="material-symbols-outlined text-[20px]">
                              {act.type === 'review' ? 'rate_review' : act.type === 'translation' ? 'translate' : 'link'}
                            </span>
                          </div>
                          <div>
                            <p className="font-body-md font-bold text-on-surface text-xs">{act.summary}</p>
                            <p className="font-mono text-code-sm text-on-surface-variant text-[11px] uppercase">{act.type}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="inline-block px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-tertiary-container text-on-tertiary-container">
                            Logged
                          </span>
                          <p className="font-body-sm text-on-surface-variant text-[10px] mt-1">
                            {act.timestamp ? new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                          </p>
                        </div>
                      </Link>
                    )
                  })
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

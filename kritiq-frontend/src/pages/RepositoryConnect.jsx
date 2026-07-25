import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import RepoFilePicker from '../components/RepoFilePicker.jsx'
import { repositoryApi } from '../api/repositoryApi.js'

export default function RepositoryConnect() {
  const navigate = useNavigate()
  const [repoUrl, setRepoUrl] = useState('')
  const [repos, setRepos] = useState([])
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  // Expanded repository files state
  const [expandedRepoId, setExpandedRepoId] = useState(null)
  const [repoFilesMap, setRepoFilesMap] = useState({})
  const [loadingRepoFilesId, setLoadingRepoFilesId] = useState(null)

  const fetchRepos = async () => {
    try {
      const data = await repositoryApi.getRepos()
      setRepos(data || [])
    } catch (err) {
      console.error('Failed to fetch repositories:', err)
      let detail = err?.response?.data?.detail
      if (err?.response?.status === 401 || detail === 'Not authenticated') {
        setErrorMsg('AUTHENTICATION_REQUIRED')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRepos()
  }, [])

  const handleConnect = async (e) => {
    e.preventDefault()
    if (!repoUrl.trim()) return

    setIsSubmitting(true)
    setErrorMsg('')

    try {
      const newRepo = await repositoryApi.connectRepo(repoUrl)
      setRepos((prev) => [newRepo, ...prev])
      setRepoUrl('')
    } catch (err) {
      let detail = err?.response?.data?.detail
      if (err?.response?.status === 401 || detail === 'Not authenticated') {
        detail = 'AUTHENTICATION_REQUIRED'
      }
      setErrorMsg(typeof detail === 'string' ? detail : 'Repository connection failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleExploreFiles = async (repo) => {
    const repoId = repo.id || repo._id
    if (expandedRepoId === repoId) {
      setExpandedRepoId(null)
      return
    }

    setExpandedRepoId(repoId)

    if (!repoFilesMap[repoId]) {
      setLoadingRepoFilesId(repoId)
      try {
        const res = await repositoryApi.getRepoFiles(repo.owner, repo.name)
        setRepoFilesMap((prev) => ({ ...prev, [repoId]: res.files || [] }))
      } catch (err) {
        console.error('Failed to fetch repo files:', err)
      } finally {
        setLoadingRepoFilesId(null)
      }
    }
  }

  const handleReviewFile = async (repo, filePath) => {
    try {
      const res = await repositoryApi.getFileContent(repo.owner, repo.name, filePath)
      const ext = filePath.split('.').pop().toLowerCase()
      let language = 'python'
      if (ext === 'js' || ext === 'jsx') language = 'javascript'
      else if (ext === 'ts' || ext === 'tsx') language = 'typescript'
      else if (ext === 'go') language = 'go'
      else if (ext === 'java') language = 'java'
      else if (ext === 'rs') language = 'rust'
      else if (ext === 'cpp' || ext === 'c' || ext === 'h') language = 'cpp'

      navigate('/review', { state: { code: res.content || '', filename: filePath, language } })
    } catch (err) {
      console.error('Failed to fetch file for review:', err)
    }
  }

  const handleTranslateFile = async (repo, filePath) => {
    try {
      const res = await repositoryApi.getFileContent(repo.owner, repo.name, filePath)
      const ext = filePath.split('.').pop().toLowerCase()
      let sourceLang = 'python'
      if (ext === 'js' || ext === 'jsx') sourceLang = 'javascript'
      else if (ext === 'ts' || ext === 'tsx') sourceLang = 'typescript'
      else if (ext === 'go') sourceLang = 'go'
      else if (ext === 'java') sourceLang = 'java'
      else if (ext === 'rs') sourceLang = 'rust'
      else if (ext === 'cpp' || ext === 'c' || ext === 'h') sourceLang = 'cpp'

      navigate('/translate', { state: { code: res.content || '', filename: filePath, sourceLang } })
    } catch (err) {
      console.error('Failed to fetch file for translation:', err)
    }
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64">
        <NavBar title="Repositories" />

        <main className="mt-16 p-lg space-y-lg max-w-5xl mx-auto">
          {/* Header Description */}
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Connect GitHub Repository</h2>
            <p className="font-body-md text-on-surface-variant mt-xs text-xs">
              Link public or private GitHub repositories to allow KRITIQ's RAG engine to index your code structure.
            </p>
          </div>

          {errorMsg && (
            <div className="p-md bg-error-container/30 border border-error/50 rounded-lg text-error text-xs flex items-center justify-between gap-md">
              <div className="flex items-center gap-xs">
                <span className="material-symbols-outlined text-[18px]">lock</span>
                {errorMsg === 'AUTHENTICATION_REQUIRED' ? (
                  <span>You are not logged in. Please log in or create an account first.</span>
                ) : (
                  <span>{errorMsg}</span>
                )}
              </div>
              {errorMsg === 'AUTHENTICATION_REQUIRED' && (
                <Link
                  to="/login"
                  className="bg-error text-on-error px-md py-xs rounded font-bold text-xs hover:brightness-110 whitespace-nowrap"
                >
                  Log In Now
                </Link>
              )}
            </div>
          )}

          {/* Connect Input Box */}
          <section className="bg-surface-container border border-outline-variant rounded-xl p-xl shadow-lg">
            <form onSubmit={handleConnect} className="space-y-md">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase text-[10px]" htmlFor="repoUrl">
                GitHub Repository URL
              </label>
              
              <div className="flex flex-col sm:flex-row gap-md">
                <div className="relative flex-1 group glow-hover">
                  <div className="absolute inset-y-0 left-0 pl-md flex items-center pointer-events-none">
                    <span className="material-symbols-outlined text-body-lg text-outline">link</span>
                  </div>
                  <input
                    id="repoUrl"
                    type="url"
                    required
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/owner/repository"
                    className="w-full bg-surface-container-lowest border border-outline-variant text-on-surface rounded-lg py-md pl-xl pr-md focus:ring-1 focus:ring-primary focus:border-primary transition-all font-mono text-code-sm outline-none placeholder:text-outline/50 text-xs"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="bg-primary text-on-primary font-bold px-xl py-md rounded-lg hover:brightness-110 active:scale-[0.98] transition-all flex items-center justify-center gap-xs text-body-md disabled:opacity-50 whitespace-nowrap text-xs"
                >
                  {isSubmitting ? (
                    <>
                      <span className="material-symbols-outlined text-[18px] animate-spin">refresh</span>
                      Connecting...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-[18px]">add_link</span>
                      Connect Repo
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>

          {/* Connected Repositories List */}
          <section className="space-y-md">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-md text-body-md font-bold text-on-surface">Connected Repositories ({repos.length})</h3>
            </div>

            <div className="space-y-md">
              {loading ? (
                <div className="p-md bg-surface-container border border-outline-variant rounded-xl text-center text-on-surface-variant text-xs font-mono">
                  Loading repositories...
                </div>
              ) : repos.length === 0 ? (
                <div className="p-md bg-surface-container border border-outline-variant rounded-xl text-center text-on-surface-variant text-xs">
                  No repositories connected yet. Enter a GitHub repository URL above to connect!
                </div>
              ) : (
                repos.map((repo) => {
                  const repoId = repo.id || repo._id
                  const isExpanded = expandedRepoId === repoId
                  const files = repoFilesMap[repoId] || []
                  const isLoadingFiles = loadingRepoFilesId === repoId

                  return (
                    <div
                      key={repoId}
                      className="bg-surface-container border border-outline-variant rounded-xl overflow-hidden hover:border-primary/60 transition-all"
                    >
                      <div className="p-md flex items-center justify-between">
                        <div className="flex items-center gap-md">
                          <div className="w-10 h-10 rounded-lg bg-surface-container-high border border-outline-variant flex items-center justify-center text-primary">
                            <span className="material-symbols-outlined text-[24px]">folder_open</span>
                          </div>
                          <div>
                            <div className="flex items-center gap-sm">
                              <a
                                href={repo.repo_url}
                                target="_blank"
                                rel="noreferrer"
                                className="font-headline-md text-body-md font-bold text-on-surface hover:text-primary transition-colors text-xs"
                              >
                                {repo.owner}/{repo.name}
                              </a>
                              <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-tertiary-container text-on-tertiary-container">
                                Synced
                              </span>
                            </div>
                            <p className="font-mono text-code-sm text-on-surface-variant text-[11px] mt-xs">
                              {repo.created_at ? new Date(repo.created_at).toLocaleDateString() : 'Connected'}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-sm">
                          <button
                            onClick={() => toggleExploreFiles(repo)}
                            className="bg-primary/10 text-primary border border-primary/30 px-md py-xs rounded-lg font-bold text-xs hover:bg-primary/20 transition-colors flex items-center gap-xs"
                          >
                            <span className="material-symbols-outlined text-[16px]">folder_special</span>
                            {isExpanded ? 'Hide Files' : 'Pick Files to Review / Translate'}
                          </button>

                          <a
                            href={repo.repo_url}
                            target="_blank"
                            rel="noreferrer"
                            className="p-xs text-on-surface-variant hover:text-primary transition-colors rounded hover:bg-surface-container-high"
                            title="View on GitHub"
                          >
                            <span className="material-symbols-outlined text-[20px]">open_in_new</span>
                          </a>
                        </div>
                      </div>

                      {/* File Drawer List */}
                      {isExpanded && (
                        <div className="p-md bg-surface-container-lowest border-t border-outline-variant/40 space-y-sm">
                          <RepoFilePicker
                            files={files}
                            loading={isLoadingFiles}
                            loadingText="Fetching repository file tree recursively..."
                            emptyText="No files found in this repository."
                            labelIcon="folder_special"
                            labelText={`Files in ${repo.owner}/${repo.name}`}
                            renderFileActions={(filePath) => (
                              <div className="flex items-center gap-xs">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleReviewFile(repo, filePath)
                                  }}
                                  className="bg-primary/10 text-primary hover:bg-primary/20 border border-primary/30 px-sm py-0.5 rounded text-[10px] font-bold"
                                  title="Review this file"
                                >
                                  Review
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleTranslateFile(repo, filePath)
                                  }}
                                  className="bg-secondary/10 text-secondary hover:bg-secondary/20 border border-secondary/30 px-sm py-0.5 rounded text-[10px] font-bold"
                                  title="Translate this file"
                                >
                                  Translate
                                </button>
                              </div>
                            )}
                          />
                        </div>
                      )}
                    </div>
                  )
                })
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}

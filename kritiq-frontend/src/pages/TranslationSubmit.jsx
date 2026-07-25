import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'
import CodeEditor from '../components/CodeEditor'
import { translationApi } from '../api/translationApi.js'
import { repositoryApi } from '../api/repositoryApi.js'

export default function TranslationSubmit() {
  const navigate = useNavigate()
  const [sourceLang, setSourceLang] = useState('python')
  const [targetLang, setTargetLang] = useState('java')
  const [code, setCode] = useState(`def calculate_discount(price: float, discount_percent: float) -> float:
    if price < 0 or discount_percent < 0:
        raise ValueError("Price and discount must be positive")
    
    discount_amount = price * (discount_percent / 100.0)
    final_price = price - discount_amount
    return round(final_price, 2)
`)
  const [isTranslating, setIsTranslating] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  // Repository Selection State
  const [repos, setRepos] = useState([])
  const [selectedRepoId, setSelectedRepoId] = useState('')
  const [repoFiles, setRepoFiles] = useState([])
  const [selectedFilePath, setSelectedFilePath] = useState('')
  const [loadingFiles, setLoadingFiles] = useState(false)

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const data = await repositoryApi.getRepos()
        setRepos(data || [])
      } catch (err) {
        console.error('Failed to fetch connected repos:', err)
      }
    }
    fetchRepos()
  }, [])

  const handleRepoSelect = async (repoId) => {
    setSelectedRepoId(repoId)
    setRepoFiles([])
    setSelectedFilePath('')

    if (!repoId) return

    const selectedRepo = repos.find((r) => r.id === repoId || r._id === repoId)
    if (!selectedRepo) return

    setLoadingFiles(true)
    try {
      const res = await repositoryApi.getRepoFiles(selectedRepo.owner, selectedRepo.name)
      setRepoFiles(res.files || [])
    } catch (err) {
      console.error('Failed to fetch files for repo:', err)
    } finally {
      setLoadingFiles(false)
    }
  }

  const handleFileSelect = async (filePath) => {
    setSelectedFilePath(filePath)
    if (!filePath) return

    const selectedRepo = repos.find((r) => r.id === selectedRepoId || r._id === selectedRepoId)
    if (!selectedRepo) return

    // Auto detect source language from extension
    const ext = filePath.split('.').pop().toLowerCase()
    if (ext === 'py') setSourceLang('python')
    else if (ext === 'js' || ext === 'jsx') setSourceLang('javascript')
    else if (ext === 'ts' || ext === 'tsx') setSourceLang('typescript')
    else if (ext === 'go') setSourceLang('go')
    else if (ext === 'java') setSourceLang('java')
    else if (ext === 'rs') setSourceLang('rust')
    else if (ext === 'cpp' || ext === 'c' || ext === 'h') setSourceLang('cpp')

    try {
      const res = await repositoryApi.getFileContent(selectedRepo.owner, selectedRepo.name, filePath)
      if (res?.content) {
        setCode(res.content)
      }
    } catch (err) {
      console.error('Failed to fetch file content:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!code.trim()) return

    setIsTranslating(true)
    setErrorMsg('')

    try {
      const result = await translationApi.submitTranslation({
        source_code: code,
        source_language: sourceLang,
        target_language: targetLang
      })

      navigate(`/translate/${result.translation_id}`, {
        state: {
          initialResult: result,
          sourceCode: code,
          sourceLang,
          targetLang
        }
      })
    } catch (err) {
      console.error('Failed to submit translation:', err)
      let detail = err?.response?.data?.detail
      if (err?.response?.status === 401 || detail === 'Not authenticated') {
        detail = 'AUTHENTICATION_REQUIRED'
      }
      setErrorMsg(typeof detail === 'string' ? detail : 'Translation execution error.')
    } finally {
      setIsTranslating(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <NavBar title="Cross-Language Translation" />

        <main className="mt-16 flex-1 flex flex-col p-lg space-y-md overflow-hidden">
          {/* Connected Repo File Selector Bar */}
          {repos.length > 0 && (
            <div className="p-md bg-surface-container-high border border-outline-variant/60 rounded-xl flex flex-wrap items-center gap-md flex-shrink-0">
              <div className="flex items-center gap-xs text-secondary font-bold text-xs font-mono">
                <span className="material-symbols-outlined text-[18px]">folder_open</span>
                Connected Repositories:
              </div>

              {/* Repo Selector Dropdown */}
              <select
                value={selectedRepoId}
                onChange={(e) => handleRepoSelect(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant rounded px-sm py-1 font-mono text-code-sm text-on-surface outline-none focus:border-primary text-xs"
              >
                <option value="">-- Choose Repository --</option>
                {repos.map((repo) => (
                  <option key={repo.id || repo._id} value={repo.id || repo._id}>
                    {repo.owner}/{repo.name}
                  </option>
                ))}
              </select>

              {/* File Selector Dropdown */}
              {selectedRepoId && (
                <div className="flex items-center gap-xs flex-1 max-w-md">
                  <span className="material-symbols-outlined text-outline text-[16px]">subdirectory_arrow_right</span>
                  <select
                    value={selectedFilePath}
                    onChange={(e) => handleFileSelect(e.target.value)}
                    disabled={loadingFiles}
                    className="w-full bg-surface-container-lowest border border-outline-variant rounded px-sm py-1 font-mono text-code-sm text-on-surface outline-none focus:border-primary text-xs disabled:opacity-50 truncate"
                  >
                    <option value="">{loadingFiles ? 'Indexing all repository files...' : '-- Pick File to Translate --'}</option>
                    {repoFiles.map((file) => (
                      <option key={file} value={file}>
                        {file}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )}

          {/* Options Bar */}
          <div className="flex flex-wrap items-center justify-between gap-md bg-surface-container border border-outline-variant p-md rounded-xl flex-shrink-0">
            <div className="flex items-center gap-md">
              <div>
                <label className="font-label-caps text-on-surface-variant uppercase text-[10px] block mb-1">
                  Source Language
                </label>
                <select
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  className="bg-surface-container-lowest border border-outline-variant rounded px-sm py-1 font-mono text-code-sm text-on-surface outline-none focus:border-primary text-xs"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="go">Go</option>
                  <option value="java">Java</option>
                  <option value="rust">Rust</option>
                  <option value="cpp">C++</option>
                </select>
              </div>

              <div className="flex items-center pt-4">
                <span className="material-symbols-outlined text-outline text-[20px]">arrow_forward</span>
              </div>

              <div>
                <label className="font-label-caps text-on-surface-variant uppercase text-[10px] block mb-1">
                  Target Language
                </label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="bg-surface-container-lowest border border-outline-variant rounded px-sm py-1 font-mono text-code-sm text-on-surface outline-none focus:border-primary text-xs"
                >
                  <option value="java">Java</option>
                  <option value="go">Go</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="rust">Rust</option>
                  <option value="cpp">C++</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={isTranslating}
              className="bg-secondary text-on-secondary font-bold px-lg py-sm rounded-lg hover:brightness-110 active:scale-[0.98] transition-all flex items-center gap-xs text-body-sm disabled:opacity-50"
            >
              {isTranslating ? (
                <>
                  <span className="material-symbols-outlined text-[18px] animate-spin">refresh</span>
                  Translating Code...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">translate</span>
                  Translate Code
                </>
              )}
            </button>
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

          {/* Monaco Source Code Input Container */}
          <div className="flex-1 min-h-0">
            <CodeEditor
              code={code}
              onChange={setCode}
              language={sourceLang}
              height="100%"
            />
          </div>
        </main>
      </div>
    </div>
  )
}

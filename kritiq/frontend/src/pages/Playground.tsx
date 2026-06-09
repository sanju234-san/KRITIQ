import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Database, 
  BrainCircuit, 
  Github, 
  Key, 
  Chrome, 
  AlertCircle, 
  Loader2, 
  RefreshCw, 
  ArrowLeft, 
  ShieldCheck,
  Check,
  X
} from "lucide-react";

interface ServiceStatus {
  status: "OK" | "ERROR" | "WARNING";
  error?: string | null;
  username?: string;
}

interface OAuthConfig {
  client_id?: string;
  is_configured: boolean;
  has_secret: boolean;
  callback_url: string;
}

interface JWTConfig {
  is_configured: boolean;
  length_ok: boolean;
}

interface PlaygroundData {
  mongodb: ServiceStatus;
  groq: ServiceStatus;
  github_token: ServiceStatus;
  github_oauth: OAuthConfig;
  google_oauth: OAuthConfig;
  jwt: JWTConfig;
}

export default function Playground() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PlaygroundData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/playground/test-keys");
      if (response.ok) {
        const result = await response.json();
        setData(result);
      } else {
        setError(`Failed to fetch credentials status. Server returned ${response.status}`);
      }
    } catch (err: any) {
      setError(err?.message || "An unexpected error occurred while communicating with the server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col relative overflow-hidden">
      {/* Visual background accents */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-purple-900/10 blur-[120px] pointer-events-none animate-pulse" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-cyan-900/10 blur-[120px] pointer-events-none animate-pulse" />

      {/* Header */}
      <header className="border-b border-zinc-800/60 bg-zinc-900/20 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <button 
            onClick={() => navigate(-1)} 
            className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200 transition-colors font-mono text-xs"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back</span>
          </button>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-ping" />
            <span className="text-xs font-mono text-zinc-400 select-none">Playground Active</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-12">
        <div className="mb-10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-purple-400 via-zinc-200 to-cyan-400 bg-clip-text text-transparent mb-2">
                Integration Playground
              </h1>
              <p className="text-zinc-400 text-sm max-w-xl">
                Diagnostic console to verify that the frontend, FastAPI backend, databases, and OAuth app configurations are connected and valid.
              </p>
            </div>
            
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl px-5 py-3 font-semibold shadow-lg shadow-purple-500/20 hover:shadow-purple-500/35 transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none font-mono text-xs"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Validating Keys...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  <span>Run Validation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-8 rounded-xl border border-red-500/30 bg-red-500/10 p-5 flex items-start gap-3 text-red-200 text-sm backdrop-blur-md">
            <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold mb-1">Communication Error</h3>
              <p>{error}</p>
              <p className="text-xs text-red-400/80 mt-2">
                Make sure your FastAPI server is running locally (usually on port 8000) and that Vite is successfully proxying requests.
              </p>
            </div>
          </div>
        )}

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* 1. MongoDB Cluster Connection */}
          <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 backdrop-blur-xl p-6 transition-all duration-300 hover:border-zinc-700/60 hover:shadow-lg hover:shadow-purple-500/5 group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-zinc-800/60 flex items-center justify-center text-green-400 border border-zinc-700/40">
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200">MongoDB Database</h3>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase">Persistence Layer</span>
                  </div>
                </div>

                {data ? (
                  data.mongodb.status === "OK" ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-1 text-xs font-medium text-green-400 border border-green-500/20">
                      <Check className="h-3.5 w-3.5" /> Connected
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-400 border border-red-500/20">
                      <X className="h-3.5 w-3.5" /> Offline
                    </span>
                  )
                ) : (
                  <div className="h-6 w-16 bg-zinc-800 rounded animate-pulse" />
                )}
              </div>

              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Database Name</span>
                  <span className="text-zinc-300">{data ? "kritiq" : "Checking..."}</span>
                </div>
                {data && data.mongodb.status === "ERROR" && (
                  <div className="rounded bg-red-950/30 border border-red-800/40 p-3 text-red-300 font-sans mt-2 whitespace-normal break-words">
                    <strong>Error:</strong> {data.mongodb.error}
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-6 text-[11px] text-zinc-500">
              Validates that your credentials in <code className="text-zinc-400">MONGODB_URI</code> are correct and that Atlas has whitelisted your IP.
            </div>
          </div>

          {/* 2. Groq LLM Inference API */}
          <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 backdrop-blur-xl p-6 transition-all duration-300 hover:border-zinc-700/60 hover:shadow-lg hover:shadow-purple-500/5 group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-zinc-800/60 flex items-center justify-center text-purple-400 border border-zinc-700/40">
                    <BrainCircuit className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200">Groq LLM Service</h3>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase">Agent Brain</span>
                  </div>
                </div>

                {data ? (
                  data.groq.status === "OK" ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-1 text-xs font-medium text-green-400 border border-green-500/20">
                      <Check className="h-3.5 w-3.5" /> Online
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-400 border border-red-500/20">
                      <X className="h-3.5 w-3.5" /> Error
                    </span>
                  )
                ) : (
                  <div className="h-6 w-16 bg-zinc-800 rounded animate-pulse" />
                )}
              </div>

              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Test Model</span>
                  <span className="text-zinc-300">llama3-8b-8192</span>
                </div>
                {data && data.groq.status === "ERROR" && (
                  <div className="rounded bg-red-950/30 border border-red-800/40 p-3 text-red-300 font-sans mt-2 whitespace-normal break-words">
                    <strong>Error:</strong> {data.groq.error}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 text-[11px] text-zinc-500">
              Validates the <code className="text-zinc-400">GROQ_API_KEY</code> by executing a simple completion task.
            </div>
          </div>

          {/* 3. GitHub PAT (Personal Access Token) */}
          <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 backdrop-blur-xl p-6 transition-all duration-300 hover:border-zinc-700/60 hover:shadow-lg hover:shadow-purple-500/5 group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-zinc-800/60 flex items-center justify-center text-cyan-400 border border-zinc-700/40">
                    <Github className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200">GitHub API Integration</h3>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase">Repository Token</span>
                  </div>
                </div>

                {data ? (
                  data.github_token.status === "OK" ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-1 text-xs font-medium text-green-400 border border-green-500/20">
                      <Check className="h-3.5 w-3.5" /> Authenticated
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-400 border border-red-500/20">
                      <X className="h-3.5 w-3.5" /> Unauthorized
                    </span>
                  )
                ) : (
                  <div className="h-6 w-16 bg-zinc-800 rounded animate-pulse" />
                )}
              </div>

              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Connected User</span>
                  <span className="text-cyan-400 font-semibold">
                    {data && data.github_token.username ? `@${data.github_token.username}` : data ? "None" : "Checking..."}
                  </span>
                </div>
                {data && data.github_token.status === "ERROR" && (
                  <div className="rounded bg-red-950/30 border border-red-800/40 p-3 text-red-300 font-sans mt-2 whitespace-normal break-words">
                    <strong>Error:</strong> {data.github_token.error}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 text-[11px] text-zinc-500">
              Validates your <code className="text-zinc-400">GITHUB_TOKEN</code> to ensure the agent can read pull requests and write line-by-line review comments.
            </div>
          </div>

          {/* 4. JWT & Encryption Configuration */}
          <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 backdrop-blur-xl p-6 transition-all duration-300 hover:border-zinc-700/60 hover:shadow-lg hover:shadow-purple-500/5 group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-zinc-800/60 flex items-center justify-center text-yellow-400 border border-zinc-700/40">
                    <Key className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200">JWT Security Token</h3>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase">Session Cookies</span>
                  </div>
                </div>

                {data ? (
                  data.jwt.is_configured && data.jwt.length_ok ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-1 text-xs font-medium text-green-400 border border-green-500/20">
                      <Check className="h-3.5 w-3.5" /> Secure
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-yellow-500/10 px-2.5 py-1 text-xs font-medium text-yellow-400 border border-yellow-500/20">
                      <AlertCircle className="h-3.5 w-3.5" /> Check Key
                    </span>
                  )
                ) : (
                  <div className="h-6 w-16 bg-zinc-800 rounded animate-pulse" />
                )}
              </div>

              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Configured</span>
                  <span className={data?.jwt.is_configured ? "text-green-400" : "text-yellow-400"}>
                    {data ? (data.jwt.is_configured ? "Yes" : "No") : "Checking..."}
                  </span>
                </div>
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Security Strength</span>
                  <span className={data?.jwt.length_ok ? "text-green-400" : "text-yellow-400"}>
                    {data ? (data.jwt.length_ok ? "Robust (>=32 chars)" : "Weak/Incomplete") : "Checking..."}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 text-[11px] text-zinc-500">
              Validates your <code className="text-zinc-400">JWT_SECRET_KEY</code> configuration used to sign session cookies securely.
            </div>
          </div>

          {/* 5. GitHub OAuth Provider */}
          <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 backdrop-blur-xl p-6 transition-all duration-300 hover:border-zinc-700/60 hover:shadow-lg hover:shadow-purple-500/5 group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-zinc-800/60 flex items-center justify-center text-zinc-400 border border-zinc-700/40">
                    <ShieldCheck className="h-5 w-5 text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200">GitHub OAuth App</h3>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase">Authentication Client</span>
                  </div>
                </div>

                {data ? (
                  data.github_oauth.is_configured && data.github_oauth.has_secret ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-1 text-xs font-medium text-green-400 border border-green-500/20">
                      <Check className="h-3.5 w-3.5" /> Configured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-yellow-500/10 px-2.5 py-1 text-xs font-medium text-yellow-400 border border-yellow-500/20">
                      <AlertCircle className="h-3.5 w-3.5" /> Not Setup
                    </span>
                  )
                ) : (
                  <div className="h-6 w-16 bg-zinc-800 rounded animate-pulse" />
                )}
              </div>

              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Client ID</span>
                  <span className="text-zinc-300 truncate max-w-[180px]">
                    {data ? data.github_oauth.client_id : "Checking..."}
                  </span>
                </div>
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Client Secret Configured</span>
                  <span className={data?.github_oauth.has_secret ? "text-green-400" : "text-yellow-400"}>
                    {data ? (data.github_oauth.has_secret ? "Yes" : "No") : "Checking..."}
                  </span>
                </div>
                <div className="flex flex-col gap-1 pt-1">
                  <span className="text-zinc-500">Expected Callback URL</span>
                  <span className="text-zinc-400 bg-zinc-950/60 p-1.5 rounded border border-zinc-900 overflow-x-auto text-[10px]">
                    {data ? data.github_oauth.callback_url : "Loading..."}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 text-[11px] text-zinc-500">
              Credentials mapped to <code className="text-zinc-400">GITHUB_CLIENT_ID</code> and secret in settings. Used to enable GitHub logins.
            </div>
          </div>

          {/* 6. Google OAuth Provider */}
          <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/30 backdrop-blur-xl p-6 transition-all duration-300 hover:border-zinc-700/60 hover:shadow-lg hover:shadow-purple-500/5 group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-zinc-800/60 flex items-center justify-center text-zinc-400 border border-zinc-700/40">
                    <Chrome className="h-5 w-5 text-orange-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200">Google OAuth Client</h3>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase">Authentication Client</span>
                  </div>
                </div>

                {data ? (
                  data.google_oauth.is_configured && data.google_oauth.has_secret ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/10 px-2.5 py-1 text-xs font-medium text-green-400 border border-green-500/20">
                      <Check className="h-3.5 w-3.5" /> Configured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-yellow-500/10 px-2.5 py-1 text-xs font-medium text-yellow-400 border border-yellow-500/20">
                      <AlertCircle className="h-3.5 w-3.5" /> Not Setup
                    </span>
                  )
                ) : (
                  <div className="h-6 w-16 bg-zinc-800 rounded animate-pulse" />
                )}
              </div>

              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Client ID</span>
                  <span className="text-zinc-300 truncate max-w-[180px]">
                    {data ? data.google_oauth.client_id : "Checking..."}
                  </span>
                </div>
                <div className="flex justify-between border-b border-zinc-800/40 pb-2">
                  <span className="text-zinc-500">Client Secret Configured</span>
                  <span className={data?.google_oauth.has_secret ? "text-green-400" : "text-yellow-400"}>
                    {data ? (data.google_oauth.has_secret ? "Yes" : "No") : "Checking..."}
                  </span>
                </div>
                <div className="flex flex-col gap-1 pt-1">
                  <span className="text-zinc-500">Expected Redirect URL</span>
                  <span className="text-zinc-400 bg-zinc-950/60 p-1.5 rounded border border-zinc-900 overflow-x-auto text-[10px]">
                    {data ? data.google_oauth.callback_url : "Loading..."}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 text-[11px] text-zinc-500">
              Credentials mapped to <code className="text-zinc-400">GOOGLE_CLIENT_ID</code> and secret in settings. Used to enable Google logins.
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

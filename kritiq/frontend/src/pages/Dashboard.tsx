import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Play,
  GitBranch,
  Globe,
  CheckCircle2,
  Loader2,
  XCircle,
  Clock,
} from "lucide-react";

const STATUS_MAP = {
  complete: {
    icon: CheckCircle2,
    label: "Complete",
    cls: "text-emerald-400 bg-emerald-400/10 ring-emerald-400/20",
  },
  running: {
    icon: Loader2,
    label: "Running",
    cls: "text-cyan-400 bg-cyan-400/10 ring-cyan-400/20",
  },
  failed: {
    icon: XCircle,
    label: "Failed",
    cls: "text-red-400 bg-red-400/10 ring-red-400/20",
  },
  pending: {
    icon: Clock,
    label: "Pending",
    cls: "text-zinc-400 bg-zinc-400/10 ring-zinc-400/20",
  },
};

const getRepoName = (url: string) => {
  try {
    const cleaned = url.replace(/https?:\/\/(www\.)?github\.com\//, "");
    return cleaned;
  } catch {
    return url;
  }
};

const formatTimeAgo = (dateStr: string) => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [repoUrl, setRepoUrl] = useState("");
  const [liveUrl, setLiveUrl] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async () => {
    try {
      const response = await fetch("/api/reports/recent");
      if (response.ok) {
        const data = await response.json();
        setReports(data);
      }
    } catch (err) {
      console.error("Failed to fetch recent reports:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
    const interval = setInterval(fetchReports, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRun = async () => {
    if (!repoUrl.trim()) return;
    setRunning(false);
    setRunning(true);
    setError(null);
    try {
      const response = await fetch("/api/reports/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          live_url: liveUrl.trim() || null,
          commit_sha: "main",
        }),
      });
      if (response.ok) {
        const result = await response.json();
        navigate(`/pipeline/${result.report_id}`);
      } else {
        const errData = await response.json().catch(() => ({ detail: "Unknown error" }));
        setError(errData.detail || "Failed to trigger analysis. Please try again.");
      }
    } catch (err: any) {
      setError(err?.message || "An error occurred while connecting to the backend.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-10 space-y-10 animate-fade-in">
      {/* ── Hero / Input Card ─────────────────────────── */}
      <section className="rounded-2xl border border-zinc-800/60 bg-zinc-900/50 p-8 shadow-xl shadow-black/30">
        <h1 className="text-2xl font-semibold tracking-tight mb-1">
          Run a review
        </h1>
        <p className="text-sm text-zinc-500 mb-6">
          Paste a GitHub repo URL to begin an autonomous code audit.
        </p>

        <div className="space-y-4">
          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-xs font-mono text-red-400">
              {error}
            </div>
          )}

          {/* Repo URL */}
          <div className="relative">
            <GitBranch className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
            <input
              id="repo-url-input"
              type="text"
              placeholder="https://github.com/owner/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="w-full rounded-xl border border-zinc-700/60 bg-zinc-800/50 py-3 pl-11 pr-4 font-mono text-sm text-zinc-200 placeholder:text-zinc-600 focus:border-purple-500/60 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all"
            />
          </div>

          {/* Live URL (optional) */}
          <div className="relative">
            <Globe className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
            <input
              id="live-url-input"
              type="text"
              placeholder="https://my-app.vercel.app  (optional)"
              value={liveUrl}
              onChange={(e) => setLiveUrl(e.target.value)}
              className="w-full rounded-xl border border-zinc-700/60 bg-zinc-800/50 py-3 pl-11 pr-4 font-mono text-sm text-zinc-200 placeholder:text-zinc-600 focus:border-cyan-500/60 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>

          {/* CTA */}
          <button
            id="run-kritiq-button"
            onClick={handleRun}
            disabled={running}
            className="group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-500 py-3 text-sm font-semibold text-white shadow-lg shadow-purple-600/25 hover:shadow-purple-600/40 hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            {running ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Initializing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                <span>Run KRITIQ</span>
              </>
            )}
          </button>
        </div>
      </section>

      {/* ── Recent Reviews ────────────────────────────── */}
      <section>
        <h2 className="text-lg font-semibold tracking-tight mb-4">
          Recent reviews
        </h2>

        <div className="space-y-3 stagger">
          {loading ? (
            <div className="flex items-center justify-center py-10 text-zinc-500">
              <Loader2 className="h-5 w-5 animate-spin mr-2" />
              <span>Loading reviews...</span>
            </div>
          ) : reports.length === 0 ? (
            <div className="rounded-xl border border-dashed border-zinc-800/80 bg-zinc-900/10 p-10 text-center text-sm text-zinc-500">
              No recent reviews found. Paste a GitHub repo URL above to run your first review!
            </div>
          ) : (
            reports.map((r) => {
              const s = STATUS_MAP[r.status as keyof typeof STATUS_MAP] || STATUS_MAP.pending;
              const Icon = s.icon;
              return (
                <button
                  key={r.id}
                  id={`review-${r.id}`}
                  onClick={() =>
                    navigate(
                      r.status === "running" || r.status === "pending"
                        ? `/pipeline/${r.id}`
                        : `/report/${r.id}`
                    )
                  }
                  className="animate-slide-up group flex w-full items-center gap-4 rounded-xl border border-zinc-800/50 bg-zinc-900/40 px-5 py-4 text-left hover:border-zinc-700/70 hover:bg-zinc-800/40 transition-all"
                >
                  {/* Repo & SHA */}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-zinc-200 truncate group-hover:text-white transition-colors">
                      {getRepoName(r.repo_url)}
                    </p>
                    <p className="font-mono text-xs text-zinc-500 mt-0.5">
                      {r.commit_sha ? r.commit_sha.slice(0, 7) : "main"}
                    </p>
                  </div>

                  {/* Metrics */}
                  {r.status === "complete" && (
                    <div className="hidden sm:flex items-center gap-3 text-xs font-mono text-zinc-500">
                      <span>
                        <span className="text-amber-400">{r.flags ? r.flags.length : 0}</span> flags
                      </span>
                      <span>
                        <span className="text-emerald-400">{r.fixes ? r.fixes.length : 0}</span> fixes
                      </span>
                    </div>
                  )}

                  {/* Status badge */}
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${s.cls}`}
                  >
                    <Icon
                      className={`h-3.5 w-3.5 ${
                        r.status === "running" ? "animate-spin" : ""
                      }`}
                    />
                    {s.label}
                  </span>

                  {/* Timestamp */}
                  <span className="hidden md:block text-xs text-zinc-600 font-mono w-24 text-right shrink-0">
                    {formatTimeAgo(r.created_at)}
                  </span>
                </button>
              );
            })
          )}
        </div>
      </section>
    </div>
  );
}

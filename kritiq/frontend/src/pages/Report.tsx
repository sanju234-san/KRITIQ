import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ShieldAlert,
  Bug,
  Paintbrush,
  Zap,
  BookOpen,
  CheckCircle2,
  FileCode2,
  GitCommit,
  Loader2,
  ArrowLeft,
  Image as ImageIcon,
} from "lucide-react";

interface FlaggedIssue {
  id: string;
  file_path: string;
  line_number: number;
  severity: "critical" | "high" | "medium" | "low" | "info";
  category: "security" | "bug" | "style" | "performance" | "docs";
  description: string;
  suggested_fix: string;
}

interface Fix {
  id: string;
  issue_id: string;
  original_code: string;
  fixed_code: string;
  explanation: string;
  validated: boolean;
  commit_sha?: string;
}

interface ReportData {
  id: string;
  repo_url: string;
  commit_sha: string;
  flags: FlaggedIssue[];
  fixes: Fix[];
  readme_path?: string | null;
  screenshot_paths: string[];
  uml_path?: string | null;
  summary?: string | null;
  status: string;
}

/* ── Mock report data fallback ────────────────────────── */
const MOCK_REPORT: ReportData = {
  id: "rpt-mock",
  repo_url: "https://github.com/octocat/hello-world",
  commit_sha: "a3f8c2d",
  summary:
    "KRITIQ reviewed 12 files and found 5 issues across 3 categories. 3 fixes were auto-committed.",
  flags: [
    {
      id: "f1",
      file_path: "config.py",
      line_number: 14,
      severity: "critical",
      category: "security",
      description: "Hardcoded API key exposed in plain text",
      suggested_fix: "Move to environment variable using os.getenv()",
    },
    {
      id: "f2",
      file_path: "main.py",
      line_number: 42,
      severity: "high",
      category: "bug",
      description: "Uncaught exception in async handler — missing await",
      suggested_fix: "Add 'await' keyword before the async call",
    },
    {
      id: "f3",
      file_path: "main.py",
      line_number: 78,
      severity: "medium",
      category: "performance",
      description: "N+1 query inside for-loop — use batch fetch",
      suggested_fix: "Refactor to single bulk query outside the loop",
    },
    {
      id: "f4",
      file_path: "utils/helpers.py",
      line_number: 12,
      severity: "low",
      category: "style",
      description: "Function exceeds 45 lines — consider refactoring",
      suggested_fix: "Extract helper functions for clarity",
    },
    {
      id: "f5",
      file_path: "db/connection.py",
      line_number: 5,
      severity: "high",
      category: "security",
      description: "SQL query built with string concatenation — injection risk",
      suggested_fix: "Use parameterized query with placeholders",
    },
  ],
  fixes: [
    {
      id: "x1",
      issue_id: "f1",
      original_code: 'API_KEY = "sk-abc123xyz789"',
      fixed_code: 'API_KEY = os.getenv("API_KEY")',
      commit_sha: "b72e1a0",
      validated: true,
      explanation: "Extract secret key to environment variables (.env)."
    },
    {
      id: "x2",
      issue_id: "f2",
      original_code: "result = fetch_data(url)",
      fixed_code: "result = await fetch_data(url)",
      commit_sha: "c93d2b1",
      validated: true,
      explanation: "Add await keyword before async call."
    },
    {
      id: "x3",
      issue_id: "f5",
      original_code: 'query = "SELECT * FROM users WHERE id=" + user_id',
      fixed_code: 'query = "SELECT * FROM users WHERE id=%s"\ncursor.execute(query, (user_id,))',
      commit_sha: "d04e3c2",
      validated: true,
      explanation: "Use parameterized query with placeholders."
    },
  ],
  screenshot_paths: [],
  status: "complete",
};

/* ── Severity config ──────────────────────────────── */
const SEV = {
  critical: { color: "text-red-400", bg: "bg-red-400/10", ring: "ring-red-400/20", icon: ShieldAlert },
  high: { color: "text-orange-400", bg: "bg-orange-400/10", ring: "ring-orange-400/20", icon: AlertTriangle },
  medium: { color: "text-yellow-400", bg: "bg-yellow-400/10", ring: "ring-yellow-400/20", icon: Bug },
  low: { color: "text-blue-400", bg: "bg-blue-400/10", ring: "ring-blue-400/20", icon: Paintbrush },
  info: { color: "text-zinc-400", bg: "bg-zinc-400/10", ring: "ring-zinc-400/20", icon: BookOpen },
};

const CAT_ICON: Record<string, React.ElementType> = {
  security: ShieldAlert,
  bug: Bug,
  style: Paintbrush,
  performance: Zap,
  docs: BookOpen,
};

export default function Report() {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reportId) return;

    // Fallback for mock IDs
    if (reportId.startsWith("rpt-")) {
      setReport(MOCK_REPORT);
      setLoading(false);
      return;
    }

    const fetchReport = async () => {
      try {
        const response = await fetch(`/api/reports/${reportId}`);
        if (response.ok) {
          const data = await response.json();
          setReport(data);
        } else {
          setError(`Failed to fetch report. Backend returned status ${response.status}`);
        }
      } catch (err: any) {
        setError(err?.message || "An unexpected error occurred while loading the report.");
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [reportId]);

  const countBySev = (sev: "critical" | "high" | "medium" | "low" | "info") => {
    if (!report) return 0;
    return report.flags.filter((f) => f.severity === sev).length;
  };

  const getAssetUrl = (path: string) => {
    if (!path) return "";
    if (path.startsWith("http")) return path;
    return `/api/${path}`;
  };

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-zinc-950 min-h-[calc(100vh-4rem)] flex-col gap-4">
        <Loader2 className="h-8 w-8 text-purple-500 animate-spin" />
        <span className="text-zinc-400 font-mono text-xs">Retrieving Audit Report...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-20 text-center space-y-4">
        <AlertTriangle className="h-12 w-12 text-red-400 mx-auto" />
        <h2 className="text-xl font-bold text-zinc-200">Error Loading Report</h2>
        <p className="text-sm text-zinc-500">{error || "The requested audit report could not be found."}</p>
        <button
          onClick={() => navigate("/")}
          className="inline-flex items-center gap-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800/80 px-4 py-2 text-xs font-semibold font-mono text-zinc-300 mt-4"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-10 space-y-8 animate-fade-in relative overflow-hidden">
      {/* Background accents */}
      <div className="absolute top-[-10%] right-[-10%] w-[350px] h-[350px] rounded-full bg-purple-900/5 blur-[90px] pointer-events-none" />

      {/* ── Header ─────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-900 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent mb-1">
            Review Report
          </h1>
          <p className="text-xs text-zinc-500 font-mono flex items-center gap-2 flex-wrap">
            <span className="text-zinc-400">{report.repo_url}</span>
            <span className="text-zinc-600">·</span>
            <span className="text-zinc-400">{report.commit_sha}</span>
            <span className="text-zinc-600">·</span>
            <span className="text-zinc-500 text-[10px] bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800/60 font-sans">{report.id}</span>
          </p>
        </div>
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-200 transition-colors font-mono text-xs w-fit"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>dashboard</span>
        </button>
      </div>

      {/* ── Summary Cards ─────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 stagger">
        <SummaryCard
          label="Total Flags"
          value={report.flags.length}
          accent="text-amber-400"
          icon={AlertTriangle}
        />
        <SummaryCard
          label="Auto-Fixed"
          value={report.fixes.length}
          accent="text-emerald-400"
          icon={CheckCircle2}
        />
        <SummaryCard
          label="Critical / High"
          value={`${countBySev("critical")} / ${countBySev("high")}`}
          accent="text-red-400"
          icon={ShieldAlert}
        />
        <SummaryCard
          label="Medium / Low"
          value={`${countBySev("medium")} / ${countBySev("low")}`}
          accent="text-blue-400"
          icon={Bug}
        />
      </div>

      {/* ── Summary text ──────────────────────────── */}
      {report.summary && (
        <p className="text-sm text-zinc-400 leading-relaxed border-l-2 border-purple-500/40 pl-4 whitespace-pre-wrap">
          {report.summary}
        </p>
      )}

      {/* ── Diagram / UML Section ──────────────────── */}
      {report.uml_path && (
        <section className="rounded-2xl border border-zinc-800/60 bg-zinc-900/10 p-6 shadow-xl shadow-black/10">
          <div className="flex items-center gap-2 mb-4">
            <FileCode2 className="h-5 w-5 text-purple-400" />
            <h2 className="text-lg font-semibold tracking-tight text-zinc-200">System Architecture Diagram (UML)</h2>
          </div>
          <div className="rounded-xl border border-zinc-800/80 bg-zinc-950 p-6 flex justify-center items-center overflow-x-auto shadow-inner">
            <img 
              src={getAssetUrl(report.uml_path)} 
              alt="Generated Architecture UML Diagram" 
              className="max-h-[400px] object-contain hover:scale-[1.02] transition-transform duration-300"
            />
          </div>
        </section>
      )}

      {/* ── Flagged Issues Table ──────────────────── */}
      {report.flags.length > 0 ? (
        <section>
          <h2 className="text-lg font-semibold tracking-tight mb-4 text-zinc-200">
            Flagged Issues
          </h2>

          <div className="rounded-2xl border border-zinc-800/60 overflow-hidden shadow-xl shadow-black/20">
            {/* Table header */}
            <div className="hidden sm:grid grid-cols-[1.2fr_80px_95px_100px_1.5fr] gap-4 px-5 py-3 bg-zinc-900/80 border-b border-zinc-800/60 text-xs font-mono text-zinc-500 uppercase tracking-wider">
              <span>File</span>
              <span>Line</span>
              <span>Severity</span>
              <span>Category</span>
              <span>Description</span>
            </div>

            {/* Rows */}
            <div className="divide-y divide-zinc-800/40 stagger">
              {report.flags.map((flag) => {
                const sev = SEV[flag.severity] || SEV.info;
                const SevIcon = sev.icon;
                const CatIcon = CAT_ICON[flag.category] || BookOpen;

                return (
                  <div
                    key={flag.id}
                    id={`flag-${flag.id}`}
                    className="animate-slide-up grid grid-cols-1 sm:grid-cols-[1.2fr_80px_95px_100px_1.5fr] gap-2 sm:gap-4 px-5 py-4 hover:bg-zinc-800/30 transition-colors"
                  >
                    {/* File */}
                    <div className="flex items-center gap-2 min-w-0">
                      <FileCode2 className="h-4 w-4 text-zinc-600 shrink-0" />
                      <span className="font-mono text-sm text-zinc-300 truncate">
                        {flag.file_path}
                      </span>
                    </div>

                    {/* Line */}
                    <span className="font-mono text-sm text-zinc-500">
                      :{flag.line_number}
                    </span>

                    {/* Severity badge */}
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 w-fit ${sev.bg} ${sev.color} ${sev.ring}`}
                    >
                      <SevIcon className="h-3 w-3" />
                      {flag.severity}
                    </span>

                    {/* Category */}
                    <span className="inline-flex items-center gap-1 text-xs text-zinc-500">
                      <CatIcon className="h-3.5 w-3.5" />
                      {flag.category}
                    </span>

                    {/* Description */}
                    <p className="text-sm text-zinc-400 leading-snug">
                      {flag.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      ) : (
        <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/10 p-8 text-center text-zinc-500 space-y-2">
          <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto" />
          <p className="text-sm font-semibold text-zinc-300">Clean codebase!</p>
          <p className="text-xs">No quality issues or security flags were detected in the source repository.</p>
        </div>
      )}

      {/* ── Fixes Diff View ───────────────────────── */}
      {report.fixes.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold tracking-tight mb-4 text-zinc-200">
            Auto-Fixes & Corrections
          </h2>

          <div className="space-y-4 stagger">
            {report.fixes.map((fix) => {
              const matchingFlag = report.flags.find((f) => f.id === fix.issue_id);
              const filePath = matchingFlag ? matchingFlag.file_path : "unknown file";

              return (
                <div
                  key={fix.id}
                  id={`fix-${fix.id}`}
                  className="animate-slide-up rounded-2xl border border-zinc-800/60 bg-zinc-900/40 overflow-hidden shadow-lg shadow-black/10"
                >
                  {/* Fix header */}
                  <div className="flex items-center gap-3 px-5 py-3 border-b border-zinc-800/40 bg-zinc-900/60">
                    <FileCode2 className="h-4 w-4 text-zinc-500" />
                    <span className="font-mono text-sm text-zinc-300">
                      {filePath}
                    </span>
                    {fix.commit_sha && (
                      <div className="ml-auto flex items-center gap-1.5 text-xs font-mono text-zinc-500">
                        <GitCommit className="h-3.5 w-3.5" />
                        {fix.commit_sha.slice(0, 7)}
                      </div>
                    )}
                  </div>

                  {/*side-by-side diff */}
                  <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-zinc-800/40">
                    {/* Original */}
                    <div className="p-4">
                      <p className="text-[10px] font-mono text-red-400/60 uppercase tracking-wider mb-2">
                        — original
                      </p>
                      <pre className="font-mono text-xs text-red-300/80 bg-red-500/5 rounded-lg p-3 whitespace-pre-wrap overflow-x-auto">
                        {fix.original_code}
                      </pre>
                    </div>
                    {/* Fixed */}
                    <div className="p-4">
                      <p className="text-[10px] font-mono text-emerald-400/60 uppercase tracking-wider mb-2">
                        + fixed
                      </p>
                      <pre className="font-mono text-xs text-emerald-300/80 bg-emerald-500/5 rounded-lg p-3 whitespace-pre-wrap overflow-x-auto">
                        {fix.fixed_code}
                      </pre>
                    </div>
                  </div>

                  {/* Explanation panel */}
                  {fix.explanation && (
                    <div className="px-5 py-3 bg-zinc-950/60 border-t border-zinc-800/40 text-xs text-zinc-400">
                      <span className="font-semibold text-zinc-300">Explanation:</span> {fix.explanation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* ── Screenshots Panel ───────────────────────── */}
      {report.screenshot_paths.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-4">
            <ImageIcon className="h-5 w-5 text-cyan-400" />
            <h2 className="text-lg font-semibold tracking-tight text-zinc-200">Rendered Screenshots</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {report.screenshot_paths.map((path, idx) => (
              <div 
                key={idx} 
                className="rounded-xl border border-zinc-800/80 bg-zinc-900/20 overflow-hidden shadow-md flex justify-center items-center p-2 hover:border-zinc-700/60 transition-colors"
              >
                <img 
                  src={getAssetUrl(path)} 
                  alt={`Scanned application view ${idx + 1}`} 
                  className="max-h-[300px] object-contain rounded"
                />
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

/* ── Summary Card sub-component ───────────────────── */
function SummaryCard({
  label,
  value,
  accent,
  icon: Icon,
}: {
  label: string;
  value: number | string;
  accent: string;
  icon: React.ElementType;
}) {
  return (
    <div className="animate-slide-up rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-5 shadow-lg shadow-black/10">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`h-4 w-4 ${accent}`} />
        <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">
          {label}
        </span>
      </div>
      <p className={`text-2xl font-bold ${accent}`}>{value}</p>
    </div>
  );
}

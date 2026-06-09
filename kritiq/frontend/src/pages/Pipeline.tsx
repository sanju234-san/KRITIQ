import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  FileCode2,
  ScanSearch,
  ShieldCheck,
  Wrench,
  FileText,
  CheckCircle2,
  Loader2,
  Clock,
  XCircle,
  Globe,
} from "lucide-react";

/* ── Pipeline step definitions ────────────────────── */
type StepStatus = "pending" | "running" | "complete" | "failed";

interface Step {
  id: string;
  label: string;
  agent: string;
  icon: React.ElementType;
  status: StepStatus;
  duration?: number;
  error?: string;
}

const INITIAL_STEPS: Step[] = [
  { id: "clone_repo", label: "Clone & Fetch Files", agent: "GitHubService", icon: FileCode2, status: "pending" },
  { id: "code_review", label: "Code Review", agent: "CodeReviewerAgent", icon: ScanSearch, status: "pending" },
  { id: "security_audit", label: "Security Audit", agent: "SecurityAuditorAgent", icon: ShieldCheck, status: "pending" },
  { id: "auto_fix", label: "Auto Fix & Commit", agent: "AutoFixerAgent", icon: Wrench, status: "pending" },
  { id: "screenshot_uml", label: "Screenshot & UML", agent: "ScreenshotUMLAgent", icon: Globe, status: "pending" },
  { id: "readme_writer", label: "Generate Report Summary", agent: "ReadmeWriterAgent", icon: FileText, status: "pending" },
];

/* ── Mock log stream ──────────────────────────────── */
const MOCK_LOGS = [
  { ts: 0, step: "clone_repo", msg: "Cloning repo https://github.com/octocat/hello-world..." },
  { ts: 400, step: "clone_repo", msg: "Found 12 files (8 .py, 2 .ts, 1 .yml, 1 .md)" },
  { ts: 900, step: "clone_repo", msg: "✓ Files fetched" },
  { ts: 1200, step: "code_review", msg: "Analyzing main.py with Groq Llama 3.3-70B..." },
  { ts: 2000, step: "code_review", msg: "Flagged 2 issues in main.py (high: 1, medium: 1)" },
  { ts: 2500, step: "code_review", msg: "Analyzing utils/helpers.py..." },
  { ts: 3200, step: "code_review", msg: "Flagged 1 issue in utils/helpers.py (low: 1)" },
  { ts: 3600, step: "code_review", msg: "✓ Code review complete — 3 issues found" },
  { ts: 3800, step: "security_audit", msg: "Running regex secret scan..." },
  { ts: 4200, step: "security_audit", msg: "⚠ Hardcoded API key in config.py:14" },
  { ts: 4600, step: "security_audit", msg: "Checking for SQL injection patterns..." },
  { ts: 5200, step: "security_audit", msg: "✓ Security audit complete — 2 issues found" },
  { ts: 5500, step: "auto_fix", msg: "Generating fix for config.py:14 (critical/security)..." },
  { ts: 6200, step: "auto_fix", msg: "Syntax validation passed (ast.parse)" },
  { ts: 6600, step: "auto_fix", msg: "Committed fix → a3f8c2d" },
  { ts: 7200, step: "auto_fix", msg: "✓ Auto fix complete — 3/5 issues fixed" },
  { ts: 7500, step: "readme_writer", msg: "Generating README summary..." },
  { ts: 8200, step: "readme_writer", msg: "Rendering UML diagram..." },
  { ts: 8800, step: "readme_writer", msg: "✓ Report saved to MongoDB" },
];

const STATUS_ICON: Record<StepStatus, React.ElementType> = {
  pending: Clock,
  running: Loader2,
  complete: CheckCircle2,
  failed: XCircle,
};

const STATUS_STYLES: Record<StepStatus, string> = {
  pending: "text-zinc-600 border-zinc-700/50 bg-zinc-900/40",
  running: "text-purple-400 border-purple-500/40 bg-purple-500/10 animate-pulse-ring",
  complete: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
  failed: "text-red-400 border-red-500/40 bg-red-500/10",
};

const LINE_STYLES: Record<StepStatus, string> = {
  pending: "bg-zinc-800",
  running: "bg-gradient-to-b from-purple-500 to-zinc-800",
  complete: "bg-emerald-500/60",
  failed: "bg-red-500/60",
};

export default function Pipeline() {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS);
  const [logs, setLogs] = useState<{ ts: number; step: string; msg: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  /* Pipeline progress logic */
  useEffect(() => {
    if (!reportId) return;

    // Fallback: If it's a mock report ID, run simulated log streaming
    if (reportId.startsWith("rpt-")) {
      const timers: ReturnType<typeof setTimeout>[] = [];
      const stepOrder = ["clone_repo", "code_review", "security_audit", "auto_fix", "screenshot_uml", "readme_writer"];
      const stepStarts = [0, 1200, 3800, 5500, 7500, 8500];
      const stepEnds = [900, 3600, 5200, 7200, 8200, 9000];

      stepOrder.forEach((id, i) => {
        timers.push(
          setTimeout(() => {
            setSteps((prev) =>
              prev.map((s) => (s.id === id ? { ...s, status: "running" } : s))
            );
          }, stepStarts[i])
        );
        timers.push(
          setTimeout(() => {
            setSteps((prev) =>
              prev.map((s) => (s.id === id ? { ...s, status: "complete", duration: Math.round((stepEnds[i] - stepStarts[i]) / 100) / 10 } : s))
            );
          }, stepEnds[i])
        );
      });

      MOCK_LOGS.forEach((log) => {
        timers.push(
          setTimeout(() => {
            setLogs((prev) => [...prev, log]);
          }, log.ts)
        );
      });

      const redirect = setTimeout(() => {
        navigate(`/report/${reportId}`);
      }, 9500);
      timers.push(redirect);

      return () => timers.forEach(clearTimeout);
    }

    // Real API polling
    let active = true;
    let pollInterval: ReturnType<typeof setInterval>;

    const pollStatus = async () => {
      try {
        const res = await fetch(`/api/reports/${reportId}`);
        if (!res.ok) {
          if (res.status === 404) {
            setError("Review report not found. Waiting for initialization...");
          } else {
            setError("Failed to fetch pipeline status.");
          }
          return;
        }

        setError(null);
        const report = await res.json();
        if (!active) return;

        // Map database state steps to current steps
        if (report.steps && Array.isArray(report.steps)) {
          setSteps((prev) =>
            prev.map((s) => {
              const dbStep = report.steps.find((ds: any) => ds.name === s.id);
              if (dbStep) {
                return {
                  ...s,
                  status: dbStep.status as StepStatus,
                  duration: dbStep.duration_seconds,
                  error: dbStep.error_message,
                };
              }
              return s;
            })
          );
        }

        // Append live audit logs based on the real steps status
        setLogs((prev) => {
          const newLogs = [...prev];
          const addLog = (msg: string) => {
            if (!newLogs.some((l) => l.msg === msg)) {
              newLogs.push({ ts: Date.now(), step: "live", msg });
            }
          };

          if (report.status === "pending") {
            addLog("Initializing pipeline enqueuer...");
          }
          
          if (report.steps && Array.isArray(report.steps)) {
            report.steps.forEach((step: any) => {
              const label = INITIAL_STEPS.find(is => is.id === step.name)?.label || step.name;
              if (step.status === "running") {
                if (step.name === "clone_repo") {
                  addLog("Cloning repository branch and fetching source file tree...");
                } else if (step.name === "code_review") {
                  addLog("Running autonomous code review via Llama 3.3-70B...");
                } else if (step.name === "security_audit") {
                  addLog("Auditing code for OWASP patterns and hardcoded secrets...");
                } else if (step.name === "auto_fix") {
                  addLog("Generating and validating auto-fixes for critical issues...");
                } else if (step.name === "screenshot_uml") {
                  addLog("Generating codebase UML and capturing screenshot...");
                } else if (step.name === "readme_writer") {
                  addLog("Compiling final report and summary README...");
                }
              } else if (step.status === "complete") {
                addLog(`✓ Step [${label}] completed in ${step.duration_seconds || 0}s.`);
              } else if (step.status === "failed") {
                addLog(`❌ Step [${label}] failed: ${step.error_message || "Unknown error"}. Continuing pipeline...`);
              }
            });
          }

          if (report.status === "complete") {
            addLog("✓ Review pipeline completed successfully!");
            addLog("✓ Final review saved. Redirecting to report dashboard...");
          }
          if (report.status === "failed") {
            addLog(`❌ Review pipeline failed overall: ${report.error_message || "Unknown error"}`);
          }
          return newLogs;
        });

        if (report.status === "complete") {
          clearInterval(pollInterval);
          setTimeout(() => {
            if (active) navigate(`/report/${reportId}`);
          }, 2000);
        } else if (report.status === "failed") {
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error("Pipeline status polling failed:", err);
      }
    };

    pollStatus();
    pollInterval = setInterval(pollStatus, 2000);

    return () => {
      active = false;
      clearInterval(pollInterval);
    };
  }, [reportId, navigate]);

  /* Auto-scroll log panel */
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10 animate-fade-in">
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Pipeline</h1>
      <p className="text-sm text-zinc-500 mb-8 font-mono">
        report:{" "}
        <span className="text-zinc-400">{reportId}</span>
      </p>

      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-xs font-mono text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
        {/* ── Left: Step Stepper ──────────────────────── */}
        <div className="space-y-0">
          {steps.map((step, i) => {
            const IconStatus = STATUS_ICON[step.status];
            const IconAgent = step.icon;
            const isLast = i === steps.length - 1;

            return (
              <div key={step.id} className="flex gap-4" id={`pipeline-step-${step.id}`}>
                {/* Connector & circle */}
                <div className="flex flex-col items-center">
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 transition-all duration-500 ${STATUS_STYLES[step.status]}`}
                  >
                    <IconStatus
                      className={`h-4.5 w-4.5 ${
                        step.status === "running" ? "animate-spin" : ""
                      }`}
                    />
                  </div>
                  {!isLast && (
                    <div
                      className={`w-0.5 flex-1 min-h-[40px] transition-colors duration-700 ${LINE_STYLES[step.status]}`}
                    />
                  )}
                </div>

                {/* Label */}
                <div className="pb-8">
                  <div className="flex items-center gap-2 mt-2">
                    <IconAgent className="h-4 w-4 text-zinc-500" />
                    <span
                      className={`text-sm font-medium transition-colors ${
                        step.status === "running"
                          ? "text-purple-300"
                          : step.status === "complete"
                          ? "text-zinc-300"
                          : "text-zinc-500"
                      }`}
                    >
                      {step.label}
                    </span>
                    {step.duration !== undefined && step.duration !== null && (
                      <span className="text-[10px] text-zinc-500 font-mono">
                        ({step.duration}s)
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] font-mono text-zinc-600 mt-0.5 ml-6 flex flex-col gap-0.5">
                    <span>{step.agent}</span>
                    {step.error && (
                      <span className="text-[10px] text-red-400 font-mono italic">
                        Error: {step.error}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Right: Live Log Panel ──────────────────── */}
        <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/50 shadow-xl shadow-black/20 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center gap-2 px-5 py-3 border-b border-zinc-800/60">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-mono text-zinc-500 tracking-wide">
              live log output
            </span>
          </div>

          {/* Log content */}
          <div className="flex-1 overflow-y-auto p-5 font-mono text-[13px] leading-relaxed space-y-1 max-h-[420px]">
            {logs.length === 0 && (
              <span className="text-zinc-600">Waiting for pipeline to start…</span>
            )}
            {logs.map((log, i) => (
              <div key={i} className="animate-fade-in flex gap-3">
                <span className="shrink-0 text-zinc-700 select-none w-6 text-right">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span
                  className={
                    log.msg.startsWith("✓")
                      ? "text-emerald-400"
                      : log.msg.startsWith("⚠")
                      ? "text-amber-400"
                      : "text-zinc-400"
                  }
                >
                  {log.msg}
                </span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
}

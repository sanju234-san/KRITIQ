import {
  AlertCircle,
  CheckCircle2,
  Circle,
  KeyRound,
  MoreVertical,
  RefreshCw,
} from "lucide-react";

const RepositoryCard = ({ repo }) => {
  const isScanning = repo.status === "scanning";
  const isFailed = repo.status === "failed";
  const isSynced = repo.status === "synced";

  return (
    <div
      className={`flex flex-col rounded-xl border bg-[#171F2D] p-4 transition-all duration-300 ${
        isFailed
          ? "border-red-500/30 hover:border-red-500"
          : "border-[#34383d] hover:border-[#AFC8FF]/50"
      }`}
    >
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          {isFailed ? (
            <AlertCircle className="h-7 w-7 text-red-500" />
          ) : (
            <Circle
              className={`h-7 w-7 ${
                isScanning ? "fill-[#AFC8FF] text-[#AFC8FF]" : "text-[#8C909F]"
              }`}
            />
          )}

          <div>
            <h3 className="text-lg font-semibold text-white">{repo.name}</h3>

            {isScanning && (
              <div className="mt-1 flex items-center gap-2">
                <span className="h-2 w-2 animate-pulse rounded-full bg-[#AFC8FF]" />
                <span className="text-xs uppercase tracking-widest text-[#AFC8FF]">
                  Scanning...
                </span>
              </div>
            )}

            {isSynced && (
              <div className="mt-1 flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                <span className="text-xs text-[#9CA3AF]">Synced</span>
              </div>
            )}

            {isFailed && (
              <div className="mt-1 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500" />
                <span className="text-xs uppercase tracking-widest text-red-500">
                  Sync Failed
                </span>
              </div>
            )}
          </div>
        </div>

        <button>
          <MoreVertical className="h-5 w-5 text-[#8C909F]" />
        </button>
      </div>

      {/* Error */}
      {isFailed && (
        <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {repo.error}
        </div>
      )}

      {/* Details */}
      <div className="mb-4 flex-1 space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-[#8C909F]">Current Branch</span>

          <div className="flex items-center gap-2 rounded border border-[#34383d] bg-[#111418] px-2 py-1">
            <Circle className="h-3 w-3 fill-white text-white" />
            <span className="font-mono text-white">{repo.branch}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[#8C909F]">Last Commit</span>
          <span className="font-mono text-white">{repo.commit}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[#8C909F]">Last Scan</span>
          <span className="text-white">{repo.lastScan}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[#8C909F]">Language</span>
          <span className="text-white">{repo.language}</span>
        </div>
      </div>

      {/* Progress */}
      {isScanning && (
        <div className="mt-auto">
          <div className="mb-2 flex justify-between text-xs font-semibold uppercase">
            <span className="text-[#AFC8FF]">{repo.progressLabel}</span>
            <span className="text-[#AFC8FF]">{repo.progress}%</span>
          </div>

          <div className="h-1.5 overflow-hidden rounded-full bg-[#31353b]">
            <div
              className="h-full rounded-full bg-[#AFC8FF]"
              style={{ width: `${repo.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Failed */}
      {isFailed && (
        <button className="mt-auto flex h-11 items-center justify-center gap-2 rounded-lg bg-red-900/40 font-semibold text-red-300 transition hover:bg-red-900/60">
          <KeyRound className="h-4 w-4" />
          Update Credentials
        </button>
      )}

      {/* Synced */}
      {isSynced && (
        <button className="mt-auto flex h-11 items-center justify-center gap-2 rounded-lg border border-[#34383d] text-white transition hover:bg-[#252a30]">
          <RefreshCw className="h-4 w-4" />
          Re-scan Now
        </button>
      )}
    </div>
  );
};

export default RepositoryCard;
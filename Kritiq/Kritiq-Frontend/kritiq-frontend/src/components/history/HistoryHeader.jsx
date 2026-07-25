import { Download, History } from "lucide-react";

const HistoryHeader = () => {
  return (
    <div className="mb-8 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
      <div>
        <div className="mb-2 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#1E2633]">
            <History size={22} className="text-[#AFC8FF]" />
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-white">
            Activity History
          </h1>
        </div>

        <p className="text-sm text-[#8C909F]">
          Track repository scans, AI reviews, translations and system events
          across your workspace.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button className="flex h-11 items-center gap-2 rounded-xl border border-[#34383d] bg-[#171F2D] px-5 text-sm font-medium text-white transition hover:border-[#AFC8FF]">
          <Download size={16} />
          Export History
        </button>

        <button className="flex h-11 items-center gap-2 rounded-xl bg-[#AFC8FF] px-6 text-sm font-semibold text-[#002E6A] transition hover:bg-[#C6DAFF]">
          View Analytics
        </button>
      </div>
    </div>
  );
};

export default HistoryHeader;
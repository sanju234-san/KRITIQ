export default function DashboardHeader() {
  return (
    <header className="mb-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8C909F] mb-2">
            Dashboard
          </p>

          <h1 className="text-4xl font-bold text-white">
            Workspace Overview
          </h1>

          <p className="mt-3 max-w-2xl text-[#AEB5C9] leading-relaxed">
            Monitor repository health, AI-powered code reviews, recent
            development activity, and connected repositories from a single
            workspace.
          </p>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="min-w-[170px] rounded-xl border border-[#424754] bg-[#1C2025] px-5 py-4">
            <p className="text-xs uppercase tracking-wider text-[#8C909F]">
              Repositories
            </p>

            <p className="mt-2 text-2xl font-bold text-white">
              3 Connected
            </p>
          </div>

          <div className="min-w-[170px] rounded-xl border border-[#424754] bg-[#1C2025] px-5 py-4">
            <p className="text-xs uppercase tracking-wider text-[#8C909F]">
              AI Status
            </p>

            <p className="mt-2 text-2xl font-bold text-emerald-400">
              Online
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
export default function RepositoryItem({
  name,
  status,
  badge,
  type,
}) {
  return (
    <div className="flex items-center justify-between pb-5 border-b border-[#424754] last:border-0 last:pb-0">
      <div>
        <p className="text-sm font-semibold text-white">
          {name}
        </p>

        <div className="flex items-center gap-2 mt-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>

          <p className="text-xs text-[#AEB5C9]">
            {status}
          </p>
        </div>
      </div>

      <span
        className={`px-3 py-1 rounded text-xs font-semibold ${
          type === "primary"
            ? "bg-[#1F3C68] border border-[#4D8EFF] text-[#ADC6FF]"
            : "bg-[#31353B] border border-[#424754] text-[#C2C6D6]"
        }`}
      >
        {badge}
      </span>
    </div>
  );
}
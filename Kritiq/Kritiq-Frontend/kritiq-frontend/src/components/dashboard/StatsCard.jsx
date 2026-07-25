export default function StatsCard({ title, value, subtitle }) {
  const valueColor =
    title === "Repository Health"
      ? "text-emerald-500"
      : title === "AI Usage"
      ? "text-blue-400"
      : "text-white";

  return (
    <div className="bg-[#1C2025] border border-[#424754] rounded-xl p-5">
      <p className="text-xs font-bold uppercase tracking-widest text-[#8C909F] mb-2">
        {title}
      </p>

      <div className="flex items-baseline gap-3">
        <h2 className={`text-4xl font-bold ${valueColor}`}>
          {value}
        </h2>

        <p className="text-sm text-[#AEB5C9]">
          {subtitle}
        </p>
      </div>
    </div>
  );
}
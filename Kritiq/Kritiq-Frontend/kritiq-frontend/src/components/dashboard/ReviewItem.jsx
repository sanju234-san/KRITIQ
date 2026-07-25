export default function ReviewItem({
  title,
  severity,
  time,
}) {
  const severityStyles = {
    Critical:
      "bg-red-500/15 text-red-400 border border-red-500/30",
    High:
      "bg-orange-500/15 text-orange-400 border border-orange-500/30",
    Medium:
      "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",
    Low:
      "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
  };

  return (
    <div className="flex items-center justify-between py-4 border-b border-[#424754] last:border-b-0 last:pb-0 first:pt-0">
      <div>
        <h4 className="text-white font-medium">
          {title}
        </h4>

        <p className="text-sm text-[#8C909F] mt-1">
          {time}
        </p>
      </div>

      <span
        className={`px-3 py-1 rounded-md text-xs font-semibold ${
          severityStyles[severity]
        }`}
      >
        {severity}
      </span>
    </div>
  );
}
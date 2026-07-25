import { TrendingUp } from "lucide-react";

const RepositoryStats = () => {
  const stats = [
    {
      title: "Total Repositories",
      value: "12",
    },
    {
      title: "Storage Used",
      value: "4.2 GB",
    },
    {
      title: "Total Scans",
      value: "1,482",
    },
    {
      title: "Sync Health",
      value: "98%",
      trend: true,
    },
  ];

  return (
    <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {stats.map((item) => (
        <div
          key={item.title}
          className="rounded-xl border border-[#34383d] bg-[#171F2D] p-5"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-[#8C909F]">
            {item.title}
          </p>

          <div className="mt-3 flex items-center gap-2">
            <h2 className="text-3xl font-bold text-white">
              {item.value}
            </h2>

            {item.trend && (
              <TrendingUp
                size={22}
                className="text-green-500"
              />
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default RepositoryStats;
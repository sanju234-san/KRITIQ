import {
  Calendar,
  CheckCircle2,
  Filter,
  FolderGit2,
  ShieldCheck,
  Languages,
} from "lucide-react";

const filters = [
  {
    label: "Review",
    icon: <ShieldCheck size={16} />,
    active: true,
  },
  {
    label: "Translation",
    icon: <Languages size={16} />,
  },
  {
    label: "Repository",
    icon: <FolderGit2 size={16} />,
  },
  {
    label: "Success",
    icon: <CheckCircle2 size={16} className="text-green-500" />,
  },
  {
    label: "Date",
    icon: <Calendar size={16} />,
  },
];

const HistoryFilters = () => {
  return (
    <div className="mb-8 flex flex-wrap items-center gap-4">
      {/* Advanced Filter */}
      <button className="flex h-11 items-center gap-2 rounded-xl border border-[#34383d] bg-[#171F2D] px-5 text-sm font-medium text-white transition hover:border-[#AFC8FF]">
        <Filter size={16} />
        Advanced Filters
      </button>

      <div className="h-8 w-px bg-[#34383d]" />

      {filters.map((filter) => (
        <button
          key={filter.label}
          className={`flex h-11 items-center gap-2 rounded-full border px-5 text-sm font-medium transition ${
            filter.active
              ? "border-[#AFC8FF] bg-[#AFC8FF]/10 text-[#AFC8FF]"
              : "border-[#34383d] bg-[#171F2D] text-white hover:border-[#AFC8FF]"
          }`}
        >
          {filter.icon}
          {filter.label}
        </button>
      ))}

      <div className="ml-auto">
        <button className="rounded-xl border border-[#34383d] bg-[#171F2D] px-5 py-2.5 text-sm font-medium text-white transition hover:border-[#AFC8FF]">
          All Activity
        </button>
      </div>
    </div>
  );
};

export default HistoryFilters;
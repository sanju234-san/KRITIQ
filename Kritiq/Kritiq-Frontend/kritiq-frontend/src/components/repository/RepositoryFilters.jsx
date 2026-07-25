import { Filter, Search } from "lucide-react";

const RepositoryFilters = () => {
  return (
    <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center">
      {/* Search */}
      <div className="relative flex-1">
        <Search
          size={18}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8C909F]"
        />

        <input
          type="text"
          placeholder="Filter by name, language or status..."
          className="h-11 w-full rounded-xl border border-[#34383d] bg-[#171F2D] pl-10 pr-4 text-sm text-white placeholder:text-[#8C909F] focus:border-[#AFC8FF] focus:outline-none"
        />
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <button className="flex h-11 items-center gap-2 rounded-xl border border-[#34383d] bg-[#171F2D] px-5 text-sm text-white transition hover:border-[#AFC8FF]">
          <Filter size={16} />
          Type : All
        </button>

        <button className="flex h-11 items-center gap-2 rounded-xl border border-[#34383d] bg-[#171F2D] px-5 text-sm text-white transition hover:border-[#AFC8FF]">
          <Filter size={16} />
          Language : All
        </button>
      </div>
    </div>
  );
};

export default RepositoryFilters;
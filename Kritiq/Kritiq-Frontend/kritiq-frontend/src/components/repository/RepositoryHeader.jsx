import { CirclePlus } from "lucide-react";

const RepositoryHeader = () => {
  return (
    <div className="mb-8 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Repositories
        </h1>

        <p className="mt-2 text-sm text-[#8C909F]">
          Manage and monitor your connected source code assets.
        </p>
      </div>

      <button className="flex h-11 items-center justify-center gap-2 rounded-xl bg-[#AFC8FF] px-6 font-semibold text-[#002E6A] transition-all duration-200 hover:bg-[#C6DAFF]">
        <CirclePlus size={20} />
        Connect Repository
      </button>
    </div>
  );
};

export default RepositoryHeader;
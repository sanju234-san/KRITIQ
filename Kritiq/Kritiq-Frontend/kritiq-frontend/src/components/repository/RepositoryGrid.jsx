import RepositoryCard from "./RepositoryCard";

const RepositoryGrid = ({ repositories }) => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      {repositories.map((repo) => (
        <RepositoryCard key={repo.id} repo={repo} />
      ))}

      {/* Connect Repository Card */}
      <button className="flex min-h-[340px] flex-col items-center justify-center rounded-xl border-2 border-dashed border-[#34383d] bg-transparent transition-all duration-300 hover:border-[#AFC8FF] hover:bg-[#171F2D]/30">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full border border-[#34383d]">
          <span className="text-4xl text-[#8C909F]">+</span>
        </div>

        <h3 className="text-xl font-semibold text-white">
          Connect More
        </h3>

        <p className="mt-2 text-center text-sm text-[#8C909F]">
          GitHub, GitLab or Bitbucket
        </p>
      </button>
    </div>
  );
};

export default RepositoryGrid;
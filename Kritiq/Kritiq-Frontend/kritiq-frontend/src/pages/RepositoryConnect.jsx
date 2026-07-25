import RepositoryHeader from "../components/repository/RepositoryHeader";
import RepositoryFilters from "../components/repository/RepositoryFilters";
import RepositoryGrid from "../components/repository/RepositoryGrid";
import RepositoryStats from "../components/repository/RepositoryStats";
import { repositories } from "../components/repository/repositoryData";

const RepositoryConnect = () => {
  return (
    <div className="min-h-screen bg-[#101419] text-white">
      <div className="mx-auto max-w-7xl p-6">
        <RepositoryHeader />

        <RepositoryFilters />

        <RepositoryGrid repositories={repositories} />

        <RepositoryStats />
      </div>
    </div>
  );
};

export default RepositoryConnect;
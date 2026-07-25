import DashboardHeader from "../components/dashboard/DashboardHeader";
import DashboardStats from "../components/dashboard/DashboardStats";
import RecentProjects from "../components/dashboard/RecentProjects";
import RepositoryStatus from "../components/dashboard/RepositoryStatus";
import QuickReview from "../components/dashboard/QuickReview";
import RecentReviews from "../components/dashboard/RecentReviews";

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <DashboardHeader />

      <DashboardStats />

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-8">
          <RecentProjects />
        </div>

        <div className="xl:col-span-4">
          <RepositoryStatus />
        </div>

        <div className="xl:col-span-8">
          <RecentReviews />
        </div>

        <div className="xl:col-span-4">
          <QuickReview />
        </div>
      </div>
    </div>
  );
}
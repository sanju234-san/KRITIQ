import StatsCard from "./StatsCard";

export default function DashboardStats() {
  return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 mb-8">      <StatsCard
        title="Today's Reviews"
        value="12"
        subtitle="Completed & Pending"
      />

      <StatsCard
        title="Repository Health"
        value="98%"
        subtitle="3 repositories scanned"
      />

      <StatsCard
        title="AI Usage"
        value="2.4k"
        subtitle="Tokens used this session"
      />
    </div>
  );
}
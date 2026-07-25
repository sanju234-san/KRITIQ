import RepositoryItem from "./RepositoryItem";

const repositories = [
  {
    name: "kritiq-web-app",
    status: "Synced",
    badge: "2 new PRs",
    type: "primary",
  },
  {
    name: "auth-service",
    status: "Synced",
    badge: "Up to date",
    type: "default",
  },
  {
    name: "data-pipeline",
    status: "Synced",
    badge: "Up to date",
    type: "default",
  },
];

export default function RepositoryStatus() {
  return (
    <section className="space-y-4">
      <h3 className="text-xs font-bold uppercase tracking-widest text-[#8C909F]">
        Repository Status
      </h3>

      <div className="bg-[#1C2025] border border-[#424754] rounded-xl overflow-hidden">
        <div className="p-5 space-y-5">
          {repositories.map((repo) => (
            <RepositoryItem key={repo.name} {...repo} />
          ))}
        </div>
      </div>
    </section>
  );
}
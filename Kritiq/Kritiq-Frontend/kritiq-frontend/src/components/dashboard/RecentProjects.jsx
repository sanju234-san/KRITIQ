import ProjectCard from "./ProjectCard";

const repositories = [
  {
    name: "kritiq-web-app",
    language: "TypeScript",
    lastReview: "Last reviewed 2h ago",
    icon: "data_object",
  },
  {
    name: "auth-service",
    language: "Go",
    lastReview: "Last reviewed 5h ago",
    icon: "settings_ethernet",
  },
  {
    name: "data-pipeline",
    language: "Python",
    lastReview: "Last reviewed yesterday",
    icon: "database",
  },
];

export default function RecentProjects() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#8C909F]">
          Recent Projects
        </h3>

        <button className="text-sm text-[#ADC6FF] hover:underline">
          View all
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {repositories.map((repo) => (
          <ProjectCard key={repo.name} {...repo} />
        ))}

        <div className="bg-[#1C2025] border border-dashed border-[#424754] rounded-lg p-5 flex flex-col items-center justify-center text-center hover:border-[#ADC6FF] cursor-pointer transition-all">
          <div className="w-10 h-10 rounded-full bg-[#31353B] flex items-center justify-center mb-3">
            <span className="material-symbols-outlined text-[#8C909F]">
              add
            </span>
          </div>

          <p className="text-white font-semibold">
            Connect New Repository
          </p>
        </div>
      </div>
    </section>
  );
}
import {
  Bot,
  Database,
  ShieldCheck,
  BrainCircuit,
} from "lucide-react";

const technologies = [
  {
    icon: BrainCircuit,
    title: "Gemini AI",
    subtitle: "AI-powered code intelligence",
  },
  {
    icon: Bot,
    title: "FastAPI",
    subtitle: "High-performance backend APIs",
  },
  {
    icon: Database,
    title: "MongoDB",
    subtitle: "Persistent review history",
  },
  {
    icon: ShieldCheck,
    title: "JWT Security",
    subtitle: "Secure authentication",
  },
];

const BuiltFor = () => {
  return (
    <section className="border-y border-white/5 bg-[#0B1120] py-14">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Heading */}
        <div className="mb-12 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-violet-400">
            Powered By
          </p>

          <h2 className="mt-4 text-3xl font-bold text-white">
            Modern AI & Cloud Technologies
          </h2>
        </div>

        {/* Cards */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {technologies.map((item) => {
            const Icon = item.icon;

            return (
              <div
                key={item.title}
                className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:border-violet-500/30 hover:bg-violet-500/5"
              >
                <div className="mb-5 inline-flex rounded-xl bg-violet-500/10 p-3">
                  <Icon
                    size={28}
                    className="text-violet-400 transition-transform duration-300 group-hover:scale-110"
                  />
                </div>

                <h3 className="text-lg font-semibold text-white">
                  {item.title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-gray-400">
                  {item.subtitle}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default BuiltFor;
import {
  CheckCircle2,
  Sparkles,
  ShieldCheck,
  FolderGit2,
  History,
} from "lucide-react";

const reasons = [
  {
    icon: Sparkles,
    title: "Purpose-Built for Developers",
    description:
      "Review, translate, and explain code from one focused interface designed for software development workflows.",
  },
  {
    icon: FolderGit2,
    title: "Repository-Centric Workflow",
    description:
      "Manage repositories, perform AI analysis, and organize your projects without switching between multiple tools.",
  },
  {
    icon: ShieldCheck,
    title: "Secure by Design",
    description:
      "JWT authentication protects access to your account and project activities throughout the platform.",
  },
  {
    icon: History,
    title: "Persistent Activity History",
    description:
      "Access previous reviews, translations, and explanations whenever you need them.",
  },
];

const WhyKritiq = () => {
  return (
    <section
      id="why-kritiq"
      className="bg-[#0B1120] py-24"
    >
      <div className="mx-auto grid max-w-7xl gap-20 px-6 lg:grid-cols-2 lg:px-8">
        {/* Left */}
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-violet-400">
            Why KRITIQ
          </p>

          <h2 className="mt-5 text-4xl font-bold leading-tight text-white md:text-5xl">
            Built for code,
            <span className="block bg-gradient-to-r from-violet-400 to-fuchsia-300 bg-clip-text text-transparent">
              not generic conversations.
            </span>
          </h2>

          <p className="mt-8 text-lg leading-8 text-gray-400">
            KRITIQ focuses on common developer tasks—reviewing code,
            translating between programming languages, explaining complex
            logic, and maintaining a searchable history—all within a single,
            streamlined experience.
          </p>

          <div className="mt-10 space-y-5">
            {[
              "AI-powered code reviews",
              "Cross-language code translation",
              "Developer-friendly code explanations",
              "Repository management",
              "Persistent activity history",
            ].map((item) => (
              <div
                key={item}
                className="flex items-center gap-3"
              >
                <CheckCircle2
                  size={22}
                  className="text-violet-400"
                />

                <span className="text-gray-300">
                  {item}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right */}
        <div className="grid gap-6 sm:grid-cols-2">
          {reasons.map((reason) => {
            const Icon = reason.icon;

            return (
              <div
                key={reason.title}
                className="group rounded-3xl border border-white/10 bg-white/[0.03] p-7 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:border-violet-500/40"
              >
                <div className="mb-5 inline-flex rounded-2xl bg-violet-500/10 p-4">
                  <Icon
                    size={28}
                    className="text-violet-400 transition-transform duration-300 group-hover:scale-110"
                  />
                </div>

                <h3 className="text-xl font-semibold text-white">
                  {reason.title}
                </h3>

                <p className="mt-4 leading-7 text-gray-400">
                  {reason.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhyKritiq;
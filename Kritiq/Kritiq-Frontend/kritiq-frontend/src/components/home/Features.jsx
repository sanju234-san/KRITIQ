import {
  ShieldCheck,
  ArrowRightLeft,
  BrainCircuit,
  FolderGit2,
  History,
  Lock,
} from "lucide-react";

import FeatureCard from "./FeatureCard";

const features = [
  {
    icon: ShieldCheck,
    title: "AI Code Review",
    description:
      "Automatically detect bugs, security vulnerabilities, code smells, and performance issues with intelligent AI-powered analysis.",
    accent: "violet",
  },
  {
    icon: ArrowRightLeft,
    title: "Code Translation",
    description:
      "Translate source code across multiple programming languages while preserving logic and readability.",
    accent: "cyan",
  },
  {
    icon: BrainCircuit,
    title: "Code Explanation",
    description:
      "Generate simple, developer-friendly explanations for unfamiliar code to accelerate learning and onboarding.",
    accent: "emerald",
  },
  {
    icon: FolderGit2,
    title: "Repository Integration",
    description:
      "Securely connect repositories and organize code reviews from a centralized developer workspace.",
    accent: "amber",
  },
  {
    icon: History,
    title: "Review History",
    description:
      "Access previous code reviews, translations, and AI activities anytime with persistent history storage.",
    accent: "pink",
  },
  {
    icon: Lock,
    title: "Secure Authentication",
    description:
      "JWT-based authentication keeps your projects and review history protected with secure access control.",
    accent: "blue",
  },
];

const Features = () => {
  return (
    <section
      id="features"
      className="bg-[#0B1120] py-24"
    >
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Heading */}
        <div className="mx-auto mb-16 max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-violet-400">
            Features
          </p>

          <h2 className="mt-4 text-4xl font-bold text-white md:text-5xl">
            Everything Developers Need
          </h2>

          <p className="mt-6 text-lg leading-8 text-gray-400">
            KRITIQ combines AI-powered code review, intelligent translation,
            code explanation, secure repository management, and activity
            history into one modern developer platform.
          </p>
        </div>

        {/* Grid */}
        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="animate-fade-up"
              style={{
                animationDelay: `${index * 120}ms`,
                animationFillMode: "both",
              }}
            >
              <FeatureCard
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                accent={feature.accent}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Animation */}
      <style>{`
        @keyframes fade-up {
          from {
            opacity: 0;
            transform: translateY(25px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-up {
          animation: fade-up .8s ease;
        }
      `}</style>
    </section>
  );
};

export default Features;
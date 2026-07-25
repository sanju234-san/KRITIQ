import {
  LogIn,
  FolderGit2,
  ShieldCheck,
  BrainCircuit,
  History,
  ArrowRight,
} from "lucide-react";

const steps = [
  {
    icon: LogIn,
    title: "Login",
    description:
      "Create an account or sign in securely using JWT authentication.",
  },
  {
    icon: FolderGit2,
    title: "Connect Repository",
    description:
      "Connect and manage your repositories from a centralized dashboard.",
  },
  {
    icon: ShieldCheck,
    title: "AI Review",
    description:
      "Run intelligent code reviews to detect bugs, vulnerabilities, and code quality issues.",
  },
  {
    icon: BrainCircuit,
    title: "Translate & Explain",
    description:
      "Translate code between languages or generate AI-powered explanations instantly.",
  },
  {
    icon: History,
    title: "View History",
    description:
      "Access previous reviews, translations, and AI activities whenever you need them.",
  },
];

const Workflow = () => {
  return (
    <section
      id="workflow"
      className="bg-[#0B1120] py-24"
    >
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Heading */}
        <div className="mx-auto mb-20 max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-violet-400">
            Workflow
          </p>

          <h2 className="mt-4 text-4xl font-bold text-white md:text-5xl">
            From Repository to AI Insights
          </h2>

          <p className="mt-6 text-lg leading-8 text-gray-400">
            KRITIQ simplifies your development workflow into five intuitive
            steps, helping you review, understand, and improve code faster.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative grid gap-10 lg:grid-cols-5">
          {steps.map((step, index) => {
            const Icon = step.icon;

            return (
              <div
                key={step.title}
                className="relative flex flex-col items-center text-center"
              >
                {/* Connector */}
                {index !== steps.length - 1 && (
                  <div className="absolute top-10 left-[58%] hidden w-full lg:block">
                    <ArrowRight
                      size={26}
                      className="mx-auto text-violet-500/40"
                    />
                  </div>
                )}

                {/* Circle */}
                <div className="flex h-20 w-20 items-center justify-center rounded-full border border-violet-500/20 bg-violet-500/10 transition-all duration-300 hover:scale-110 hover:border-violet-400/50">
                  <Icon
                    size={34}
                    className="text-violet-400"
                  />
                </div>

                {/* Step Number */}
                <div className="mt-5 text-sm font-semibold tracking-widest text-violet-400">
                  STEP {index + 1}
                </div>

                {/* Title */}
                <h3 className="mt-2 text-xl font-semibold text-white">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="mt-4 text-sm leading-7 text-gray-400">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Workflow;
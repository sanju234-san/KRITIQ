import HeroButtons from "./HeroButtons";
import CodePreview from "./CodePreview";

const Hero = () => {
  return (
    <section className="relative overflow-hidden bg-[#0B1120]">
      {/* Background Glow */}
      <div className="absolute left-1/2 top-0 h-[550px] w-[550px] -translate-x-1/2 rounded-full bg-violet-600/10 blur-[140px]" />

      <div className="relative mx-auto flex min-h-[calc(100vh-80px)] max-w-7xl flex-col items-center gap-16 px-6 py-24 lg:flex-row lg:justify-between lg:px-8">
        {/* Left Side */}
        <div className="max-w-2xl">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center rounded-full border border-violet-500/20 bg-violet-500/10 px-4 py-2">
            <span className="text-sm font-medium text-violet-300">
              AI-Powered Developer Platform
            </span>
          </div>

          {/* Heading */}
          <h1 className="text-5xl font-extrabold leading-tight tracking-tight text-white md:text-6xl xl:text-7xl">
            Review,
            <span className="block bg-gradient-to-r from-violet-400 to-fuchsia-300 bg-clip-text text-transparent">
              Translate
            </span>
            and Explain
            <span className="block">
              Code with AI.
            </span>
          </h1>

          {/* Description */}
          <p className="mt-8 max-w-xl text-lg leading-8 text-gray-400">
            KRITIQ helps developers review code, translate between
            programming languages, generate human-friendly explanations,
            and securely manage repositories—all from one intelligent
            platform.
          </p>

          {/* Buttons */}
          <HeroButtons />

          {/* Stats */}
          <div className="mt-14 flex flex-wrap gap-10">
            <div>
              <h2 className="text-3xl font-bold text-white">3</h2>
              <p className="mt-1 text-sm text-gray-500">
                AI Services
              </p>
            </div>

            <div>
              <h2 className="text-3xl font-bold text-white">
                JWT
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Secure Authentication
              </p>
            </div>

            <div>
              <h2 className="text-3xl font-bold text-white">
                MongoDB
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Persistent History
              </p>
            </div>
          </div>
        </div>

        {/* Right Side */}
        <div className="w-full max-w-2xl">
          <CodePreview />
        </div>
      </div>
    </section>
  );
};

export default Hero;
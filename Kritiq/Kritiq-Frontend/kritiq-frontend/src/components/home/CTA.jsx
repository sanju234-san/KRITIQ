import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const CTA = () => {
  return (
    <section className="bg-[#0B1120] py-24">
      <div className="mx-auto max-w-6xl px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl border border-violet-500/20 bg-gradient-to-br from-violet-600 via-violet-700 to-indigo-900 px-8 py-16 shadow-2xl lg:px-16">
          {/* Background Glow */}
          <div className="absolute -top-20 -right-20 h-64 w-64 rounded-full bg-white/10 blur-3xl"></div>
          <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-fuchsia-500/20 blur-3xl"></div>

          <div className="relative z-10 flex flex-col items-center text-center">
            {/* Badge */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-5 py-2 backdrop-blur-md">
              <Sparkles size={16} className="text-yellow-300" />
              <span className="text-sm font-medium text-white">
                AI-Powered Developer Experience
              </span>
            </div>

            {/* Heading */}
            <h2 className="max-w-3xl text-4xl font-bold leading-tight text-white md:text-5xl">
              Start Building Better Code
              <span className="block">
                with KRITIQ Today.
              </span>
            </h2>

            {/* Description */}
            <p className="mt-6 max-w-2xl text-lg leading-8 text-violet-100">
              Review code, translate between programming languages,
              understand complex logic, and keep track of your work from
              one intelligent platform.
            </p>

            {/* Buttons */}
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link
                to="/register"
                className="group inline-flex items-center justify-center gap-2 rounded-xl bg-white px-8 py-4 font-semibold text-violet-700 transition-all duration-300 hover:-translate-y-1 hover:bg-gray-100"
              >
                Get Started
                <ArrowRight
                  size={18}
                  className="transition-transform duration-300 group-hover:translate-x-1"
                />
              </Link>

              <Link
                to="/login"
                className="inline-flex items-center justify-center rounded-xl border border-white/30 bg-white/10 px-8 py-4 font-semibold text-white backdrop-blur-md transition-all duration-300 hover:bg-white/20"
              >
                Sign In
              </Link>
            </div>

            {/* Bottom Stats */}
            <div className="mt-14 flex flex-wrap justify-center gap-10 border-t border-white/10 pt-8 text-center">
              <div>
                <h3 className="text-2xl font-bold text-white">
                  AI Review
                </h3>
                <p className="mt-1 text-sm text-violet-200">
                  Detect issues faster
                </p>
              </div>

              <div>
                <h3 className="text-2xl font-bold text-white">
                  Translation
                </h3>
                <p className="mt-1 text-sm text-violet-200">
                  Multiple languages
                </p>
              </div>

              <div>
                <h3 className="text-2xl font-bold text-white">
                  History
                </h3>
                <p className="mt-1 text-sm text-violet-200">
                  Track every activity
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
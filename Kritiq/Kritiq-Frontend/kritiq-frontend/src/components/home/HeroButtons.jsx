import { ArrowRight, Terminal } from "lucide-react";
import { FaGithub } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const HeroButtons = () => {
  const navigate = useNavigate();

  const handleConnectRepo = () => {
    navigate("/login");
  };

  const handleGetStarted = () => {
    navigate("/register");
  };

  return (
    <div className="mt-10 flex flex-col gap-4 sm:flex-row">
      {/* Get Started */}
      <button
        onClick={handleGetStarted}
        className="group flex items-center justify-center gap-2 rounded-xl bg-violet-500 px-7 py-4 font-semibold text-white shadow-lg shadow-violet-500/20 transition-all duration-300 hover:-translate-y-1 hover:bg-violet-400 hover:shadow-violet-500/40"
      >
        Get Started
        <ArrowRight
          size={18}
          className="transition-transform duration-300 group-hover:translate-x-1"
        />
      </button>

      {/* Connect Repository */}
      <button
        onClick={handleConnectRepo}
        className="group flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-7 py-4 font-semibold text-gray-200 backdrop-blur-sm transition-all duration-300 hover:border-violet-400/40 hover:bg-white/10"
      >
        <FaGithub className="text-xl transition-transform duration-300 group-hover:rotate-6" />
        Connect Repository
      </button>

      {/* CLI */}
      <button
        className="group flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-7 py-4 font-semibold text-gray-200 backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:bg-white/10"
      >
        <Terminal
          size={18}
          className="transition-transform duration-300 group-hover:scale-110"
        />
        CLI
        <span className="rounded-full bg-violet-500/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-violet-300">
          Soon
        </span>
      </button>
    </div>
  );
};

export default HeroButtons;
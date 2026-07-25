import { Terminal } from "lucide-react";

export default function AuthLogo() {
  return (
    <header className="flex flex-col items-center mb-10 text-center">
      {/* Logo */}
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-[#8b5cf6] shadow-lg shadow-purple-500/20">
        <Terminal
          size={28}
          strokeWidth={2.5}
          className="text-white"
        />
      </div>

      {/* Brand */}
      <h1 className="mb-1 text-3xl font-bold text-[#e2e8f0]">
        Kritiq
      </h1>

      <p className="text-sm font-medium tracking-wide text-gray-400">
        AI-Powered Code Intelligence
      </p>
    </header>
  );
}

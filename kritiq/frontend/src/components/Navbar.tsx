import { Link, useNavigate } from "react-router-dom";
import { ScanSearch, LogOut } from "lucide-react";
import { useAuthStore } from "../store/authStore";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, token, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
    } catch (error) {
      console.error("Logout request failed:", error);
    } finally {
      logout();
      navigate("/login");
    }
  };

  const getInitials = (name: string) => {
    if (!name) return "?";
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-purple-600 to-cyan-500 shadow-lg shadow-purple-500/20 group-hover:shadow-purple-500/40 transition-shadow">
            <ScanSearch className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              KRITIQ
            </span>
            <span className="text-[10px] font-mono text-zinc-500 tracking-widest uppercase">
              autonomous code review
            </span>
          </div>
        </Link>

        {/* Right Nav Options */}
        <div className="flex items-center gap-4">
          <Link
            to="/playground"
            className="font-mono text-xs text-zinc-400 hover:text-purple-400 transition-colors"
            title="Diagnostics Playground"
          >
            playground
          </Link>

          <div className="h-4.5 w-px bg-zinc-800/80" />

          {user && (
            <div className="flex items-center gap-3">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.name}
                  className="h-8 w-8 rounded-full border border-zinc-700/60 object-cover shadow-md"
                />
              ) : (
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 text-xs font-mono text-zinc-400 ring-1 ring-zinc-700">
                  {getInitials(user.name)}
                </div>
              )}
              <span className="hidden sm:inline text-xs font-mono text-zinc-300">
                {user.name}
              </span>
            </div>
          )}

          <div className="h-4 w-px bg-zinc-800" />

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 font-mono text-xs text-zinc-500 hover:text-red-400 transition-colors"
            title="Log Out"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden md:inline">logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

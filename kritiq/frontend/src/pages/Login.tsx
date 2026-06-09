import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { Github, ScanSearch, Loader2 } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login, isAuthenticated } = useAuthStore();
  const [verifying, setVerifying] = useState(false);
  const token = searchParams.get("token");

  useEffect(() => {
    if (token) {
      setVerifying(true);
      const verifyToken = async () => {
        try {
          const res = await fetch("/api/auth/me", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          if (res.ok) {
            const user = await res.json();
            login(token, user);
            navigate("/");
          } else {
            console.error("Token verification failed with status:", res.status);
          }
        } catch (error) {
          console.error("Token verification error:", error);
        } finally {
          setVerifying(false);
        }
      };
      verifyToken();
    } else if (isAuthenticated) {
      navigate("/");
    }
  }, [token, isAuthenticated, login, navigate]);

  const handleGitHubLogin = () => {
    window.location.href = "/api/auth/github";
  };

  const handleGoogleLogin = () => {
    window.location.href = "/api/auth/google";
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-zinc-950 px-6 py-12">
      {/* Background radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(147,51,234,0.06),transparent_60%)] pointer-events-none" />

      {verifying ? (
        <div className="text-center space-y-4 animate-fade-in">
          <Loader2 className="h-8 w-8 text-purple-500 animate-spin mx-auto" />
          <p className="font-mono text-sm text-zinc-500">
            Verifying secure session credentials...
          </p>
        </div>
      ) : (
        <div className="relative w-full max-w-md rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-8 shadow-2xl shadow-black/50 backdrop-blur-xl animate-fade-in">
          {/* Top border accent line */}
          <div className="absolute top-0 left-10 right-10 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent" />

          {/* Logo & Tagline */}
          <div className="text-center mb-10">
            <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-600 to-cyan-500 shadow-xl shadow-purple-500/20 mb-4">
              <ScanSearch className="h-7 w-7 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-purple-400 via-indigo-200 to-cyan-400 bg-clip-text text-transparent">
              KRITIQ
            </h1>
            <p className="text-xs font-mono text-zinc-500 mt-2 uppercase tracking-widest">
              autonomous code review agent
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            {/* GitHub Button */}
            <button
              onClick={handleGitHubLogin}
              className="flex w-full items-center justify-center gap-3 rounded-xl border border-zinc-800 bg-zinc-950 px-5 py-3.5 text-sm font-semibold text-zinc-200 shadow-md transition-all duration-200 hover:border-zinc-700 hover:bg-zinc-900 hover:text-white active:scale-[0.98]"
            >
              <Github className="h-5 w-5 text-zinc-200" />
              Continue with GitHub
            </button>

            {/* Google Button */}
            <button
              onClick={handleGoogleLogin}
              className="flex w-full items-center justify-center gap-3 rounded-xl border border-zinc-200 bg-white px-5 py-3.5 text-sm font-bold text-zinc-900 shadow-md transition-all duration-200 hover:bg-zinc-100 active:scale-[0.98]"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" width="24" height="24">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  fill="#EA4335"
                />
              </svg>
              Continue with Google
            </button>
          </div>

          <div className="mt-8 text-center space-y-3">
            <div>
              <span className="text-[11px] font-mono text-zinc-600 select-none">
                Secured with JSON Web Tokens (JWT)
              </span>
            </div>
            <div className="pt-2 border-t border-zinc-800/40">
              <button
                onClick={() => navigate("/playground")}
                className="text-xs font-mono text-purple-400 hover:text-purple-300 transition-colors underline decoration-dotted"
              >
                Go to Key & Connection Playground
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

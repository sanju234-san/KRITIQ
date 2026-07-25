import { Link } from "react-router-dom";
import { Mail, Lock, ArrowRight } from "lucide-react";

export default function LoginForm({
  form,
  handleChange,
  handleSubmit,
  loading,
  error,
}) {
  return (
    <>
      {error && (
        <div className="mb-6 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email */}
        <div className="space-y-2">
          <label
            htmlFor="email"
            className="block text-[11px] font-bold uppercase tracking-widest text-gray-500"
          >
            Work Email
          </label>

          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
              <Mail className="h-4 w-4 text-gray-500" />
            </div>

            <input
              id="email"
              name="email"
              type="email"
              required
              value={form.email}
              onChange={handleChange}
              placeholder="name@company.com"
              className="w-full rounded-lg border border-white/10 bg-[#0a0b0d] py-3 pl-11 pr-4 text-sm text-white placeholder:text-gray-600 focus:border-[#c4b5fd] focus:outline-none focus:ring-1 focus:ring-purple-400"
            />
          </div>
        </div>

        {/* Password */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label
              htmlFor="password"
              className="block text-[11px] font-bold uppercase tracking-widest text-gray-500"
            >
              Password
            </label>

            <button
              type="button"
              className="text-sm text-gray-400 transition-colors hover:text-white"
            >
              Forgot?
            </button>
          </div>

          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
              <Lock className="h-4 w-4 text-gray-500" />
            </div>

            <input
              id="password"
              name="password"
              type="password"
              required
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              className="w-full rounded-lg border border-white/10 bg-[#0a0b0d] py-3 pl-11 pr-4 text-sm text-white placeholder:text-gray-600 focus:border-[#c4b5fd] focus:outline-none focus:ring-1 focus:ring-purple-400"
            />
          </div>
        </div>

        {/* Continue */}
        <button
          type="submit"
          disabled={loading}
          className="group flex w-full items-center justify-center rounded-lg bg-[#c4b5fd] px-4 py-3 font-semibold text-[#1e1b4b] transition-all duration-200 hover:bg-[#b7a4fc] disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span>
            {loading ? "Signing In..." : "Continue"}
          </span>

          {!loading && (
            <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
          )}
        </button>
      </form>

      {/* Footer */}
      <div className="mt-8 flex flex-col items-center space-y-6">
        <p className="text-sm text-gray-400">
          Don't have an account?{" "}
          <Link
            to="/register"
            className="text-white transition hover:underline"
          >
            Create Account
          </Link>
        </p>
      </div>
    </>
  );
}

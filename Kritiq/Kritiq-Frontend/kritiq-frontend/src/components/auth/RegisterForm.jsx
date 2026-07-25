import { Link } from "react-router-dom";

export default function RegisterForm({
  form,
 handleChange,
  handleSubmit,
  loading,
  error,
}) {
  return (
    <>
      {error && (
        <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-300">
            Full Name
          </label>

          <input
            type="text"
            name="name"
            placeholder="Enter your full name"
            value={form.name}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-300">
            Email Address
          </label>

          <input
            type="email"
            name="email"
            placeholder="Enter your email"
            value={form.email}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-300">
            Password
          </label>

          <input
            type="password"
            name="password"
            placeholder="Create a password"
            value={form.password}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-violet-600 py-3 font-semibold text-white transition-all duration-200 hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Creating Account..." : "Create Account"}
        </button>
      </form>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-400">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-medium text-violet-400 transition hover:text-violet-300"
          >
            Sign In
          </Link>
        </p>
      </div>
    </>
  );
}
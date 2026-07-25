import { Link, NavLink } from "react-router-dom";

const HomeNavbar = () => {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-[#0B1120]/80 backdrop-blur-xl">
      <div className="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-white">
              KRITIQ
            </h1>
            <p className="-mt-1 text-[10px] uppercase tracking-widest text-gray-400">
              AI Code Intelligence
            </p>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="hidden items-center gap-10 md:flex">
          <a
            href="#features"
            className="text-sm font-medium text-gray-400 transition hover:text-white"
          >
            Features
          </a>

          <a
            href="#workflow"
            className="text-sm font-medium text-gray-400 transition hover:text-white"
          >
            Workflow
          </a>

          <a
            href="#why-kritiq"
            className="text-sm font-medium text-gray-400 transition hover:text-white"
          >
            Why KRITIQ
          </a>

          <a
            href="#footer"
            className="text-sm font-medium text-gray-400 transition hover:text-white"
          >
            Docs
          </a>
        </nav>

        {/* Buttons */}
        <div className="flex items-center gap-4">
          <NavLink
            to="/login"
            className="hidden text-sm font-medium text-gray-300 transition hover:text-white md:block"
          >
            Sign In
          </NavLink>

          <NavLink
            to="/register"
            className="rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition duration-300 hover:bg-violet-400"
          >
            Get Started
          </NavLink>
        </div>
      </div>
    </header>
  );
};

export default HomeNavbar;
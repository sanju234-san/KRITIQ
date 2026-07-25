import { Mail, Code2 } from "lucide-react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="border-t border-white/10 bg-[#0B1120]">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-violet-500/10 p-3">
                <Code2
                  size={26}
                  className="text-violet-400"
                />
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">
                  KRITIQ
                </h2>

                <p className="text-sm text-gray-500">
                  AI Code Intelligence
                </p>
              </div>
            </div>

            <p className="mt-6 leading-7 text-gray-400">
              AI-powered code review, translation, explanation,
              and repository management designed for modern
              developers.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="mb-5 text-lg font-semibold text-white">
              Product
            </h3>

            <ul className="space-y-3">
              <li>
                <a
                  href="#features"
                  className="text-gray-400 transition hover:text-violet-400"
                >
                  Features
                </a>
              </li>

              <li>
                <a
                  href="#workflow"
                  className="text-gray-400 transition hover:text-violet-400"
                >
                  Workflow
                </a>
              </li>

              <li>
                <a
                  href="#why-kritiq"
                  className="text-gray-400 transition hover:text-violet-400"
                >
                  Why KRITIQ
                </a>
              </li>
            </ul>
          </div>

          {/* Account */}
          <div>
            <h3 className="mb-5 text-lg font-semibold text-white">
              Account
            </h3>

            <ul className="space-y-3">
              <li>
                <Link
                  to="/login"
                  className="text-gray-400 transition hover:text-violet-400"
                >
                  Login
                </Link>
              </li>

              <li>
                <Link
                  to="/register"
                  className="text-gray-400 transition hover:text-violet-400"
                >
                  Register
                </Link>
              </li>

              <li>
                <Link
                  to="/dashboard"
                  className="text-gray-400 transition hover:text-violet-400"
                >
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-5 text-lg font-semibold text-white">
              Connect
            </h3>

            <div className="space-y-4">
              <div className="flex items-center gap-3 text-gray-400">
                <Mail size={18} />
                <span>support@kritiq.ai</span>
              </div>

              <div className="mt-6 flex gap-4">
                <a
                  href="#"
                  className="rounded-xl border border-white/10 p-3 text-gray-400 transition hover:border-violet-500/40 hover:text-violet-400"
                >
                  <FaGithub className="text-xl" />
                </a>

                <a
                  href="#"
                  className="rounded-xl border border-white/10 p-3 text-gray-400 transition hover:border-violet-500/40 hover:text-violet-400"
                >
                  <FaLinkedin className="text-xl" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom */}

        <div className="mt-14 flex flex-col items-center justify-between gap-5 border-t border-white/10 pt-8 text-sm text-gray-500 md:flex-row">
          <p>
            © {new Date().getFullYear()} KRITIQ. All rights reserved.
          </p>

          <p>
            Built using React, FastAPI & Gemini AI
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
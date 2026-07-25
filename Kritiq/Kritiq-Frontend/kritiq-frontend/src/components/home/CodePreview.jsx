import {
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  ArrowRightLeft,
} from "lucide-react";

const CodePreview = () => {
  return (
    <div className="relative mx-auto w-full max-w-2xl animate-[float_6s_ease-in-out_infinite]">
      {/* Glow */}
      <div className="absolute -inset-4 rounded-3xl bg-violet-500/20 blur-3xl"></div>

      {/* Editor */}
      <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#151A23] shadow-2xl shadow-black/40">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-red-500"></div>
            <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
            <div className="h-3 w-3 rounded-full bg-green-500"></div>
          </div>

          <span className="text-sm font-medium text-gray-400">
            auth_service.py — KRITIQ Review
          </span>

          <div />
        </div>

        {/* Code */}
        <div className="space-y-2 px-6 py-6 font-mono text-sm">
          <div className="flex gap-5">
            <span className="text-gray-600">12</span>
            <span>
              <span className="text-purple-400">def</span>{" "}
              <span className="text-cyan-400">login</span>()
            </span>
          </div>

          <div className="flex gap-5">
            <span className="text-gray-600">13</span>
            <span className="text-gray-300">
              token = generate_token(user)
            </span>
          </div>

          <div className="flex gap-5">
            <span className="text-gray-600">14</span>
            <span className="text-gray-300">
              return token
            </span>
          </div>

          {/* AI Review */}
          <div className="mt-8 rounded-xl border-l-4 border-violet-400 bg-[#1E2430] p-5">
            <div className="mb-4 flex items-center gap-2">
              <Sparkles
                size={18}
                className="text-violet-400"
              />

              <span className="font-semibold text-violet-300">
                KRITIQ AI
              </span>

              <span className="text-xs text-gray-500">
                reviewed just now
              </span>
            </div>

            <p className="leading-7 text-gray-300">
              Authentication flow detected.
              Consider validating token expiry before
              returning the response to improve security.
            </p>

            <div className="mt-5 space-y-3">
              <div className="flex items-center gap-3 rounded-lg bg-red-500/10 px-4 py-3">
                <AlertTriangle
                  size={18}
                  className="text-red-400"
                />

                <div>
                  <p className="font-medium text-white">
                    High Severity
                  </p>

                  <p className="text-sm text-gray-400">
                    Missing token expiration validation.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-lg bg-green-500/10 px-4 py-3">
                <CheckCircle2
                  size={18}
                  className="text-green-400"
                />

                <div>
                  <p className="font-medium text-white">
                    Suggested Fix
                  </p>

                  <p className="text-sm text-gray-400">
                    Validate JWT expiration before issuing the response.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-lg bg-cyan-500/10 px-4 py-3">
                <ArrowRightLeft
                  size={18}
                  className="text-cyan-400"
                />

                <div>
                  <p className="font-medium text-white">
                    Translation Ready
                  </p>

                  <p className="text-sm text-gray-400">
                    Convert this file to Java, C++, Go or Python.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Float animation */}
      <style>{`
        @keyframes float {
          0%,100%{
            transform:translateY(0px);
          }
          50%{
            transform:translateY(-10px);
          }
        }
      `}</style>
    </div>
  );
};

export default CodePreview;
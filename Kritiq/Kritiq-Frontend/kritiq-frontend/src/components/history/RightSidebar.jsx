import {
  Activity,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Circle,
  TrendingUp,
  Users,
} from "lucide-react";

import { historyStats, liveUsers } from "./historyData";

const RightSidebar = () => {
  return (
    <div className="space-y-6">
      {/* Activity Summary */}
      <div className="rounded-2xl border border-[#34383d] bg-[#171F2D] p-6">
        <div className="mb-5 flex items-center gap-2">
          <Activity size={18} className="text-[#AFC8FF]" />
          <h3 className="text-lg font-semibold text-white">
            Activity Summary
          </h3>
        </div>

        <div className="space-y-5">
          <div className="rounded-xl bg-[#202938] p-4">
            <p className="text-sm text-[#8C909F]">Items Logged</p>

            <h2 className="mt-1 text-3xl font-bold text-white">
              {historyStats.itemsLogged}
            </h2>

            <div className="mt-3 flex items-center gap-2 text-sm text-green-400">
              <TrendingUp size={16} />
              +18% this week
            </div>
          </div>

          <div className="rounded-xl bg-[#202938] p-4">
            <p className="text-sm text-[#8C909F]">
              Automation Success
            </p>

            <h2 className="mt-1 text-3xl font-bold text-white">
              {historyStats.automation}
            </h2>

            <div className="mt-3 flex items-center gap-2 text-sm text-green-400">
              <CheckCircle2 size={16} />
              Excellent
            </div>
          </div>
        </div>
      </div>

      {/* Live Collaborators */}
      <div className="rounded-2xl border border-[#34383d] bg-[#171F2D] p-6">
        <div className="mb-5 flex items-center gap-2">
          <Users size={18} className="text-[#AFC8FF]" />
          <h3 className="text-lg font-semibold text-white">
            Live Collaborators
          </h3>
        </div>

        <div className="space-y-4">
          {liveUsers.map((user) => (
            <div
              key={user.id}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#AFC8FF]/15 font-semibold text-[#AFC8FF]">
                  {user.initials}
                </div>

                <div>
                  <p className="font-medium text-white">
                    {user.name}
                  </p>

                  <p className="text-xs text-[#8C909F]">
                    {user.activity}
                  </p>
                </div>
              </div>

              {user.online ? (
                <Circle
                  size={10}
                  fill="#22C55E"
                  className="text-green-500"
                />
              ) : (
                <Circle
                  size={10}
                  fill="#6B7280"
                  className="text-gray-500"
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Kritiq Intelligence */}
      <div className="rounded-2xl border border-[#34383d] bg-gradient-to-br from-[#1B2230] to-[#10161F] p-6">
        <div className="mb-4 flex items-center gap-2">
          <BrainCircuit
            size={20}
            className="text-[#AFC8FF]"
          />

          <h3 className="text-lg font-semibold text-white">
            Kritiq Intelligence
          </h3>
        </div>

        <p className="text-sm leading-6 text-[#A8AFBC]">
          Your repositories show fewer security issues than last
          week. AI also detected an increase in successful review
          completion across active projects.
        </p>

        <button className="mt-6 w-full rounded-xl bg-[#AFC8FF] py-3 font-semibold text-[#002E6A] transition hover:bg-[#C6DAFF]">
          Analyze Trends
        </button>
      </div>

      {/* Quick Stats */}
      <div className="rounded-2xl border border-[#34383d] bg-[#171F2D] p-6">
        <div className="mb-5 flex items-center gap-2">
          <Bot size={18} className="text-[#AFC8FF]" />
          <h3 className="text-lg font-semibold text-white">
            AI Performance
          </h3>
        </div>

        <div className="space-y-4">
          <div>
            <div className="mb-2 flex justify-between text-sm text-[#8C909F]">
              <span>Reviews</span>
              <span>94%</span>
            </div>

            <div className="h-2 rounded-full bg-[#2C3442]">
              <div className="h-2 w-[94%] rounded-full bg-[#AFC8FF]" />
            </div>
          </div>

          <div>
            <div className="mb-2 flex justify-between text-sm text-[#8C909F]">
              <span>Translations</span>
              <span>88%</span>
            </div>

            <div className="h-2 rounded-full bg-[#2C3442]">
              <div className="h-2 w-[88%] rounded-full bg-green-500" />
            </div>
          </div>

          <div>
            <div className="mb-2 flex justify-between text-sm text-[#8C909F]">
              <span>Repository Sync</span>
              <span>97%</span>
            </div>

            <div className="h-2 rounded-full bg-[#2C3442]">
              <div className="h-2 w-[97%] rounded-full bg-purple-500" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RightSidebar;
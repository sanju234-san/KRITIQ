import {
  LayoutDashboard,
  Code2,
  Languages,
  FolderGit2,
  History,
  Settings,
  UserCircle2,
  CircleHelp,
} from "lucide-react";

import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const menuItems = [
    {
      icon: LayoutDashboard,
      label: "Dashboard",
      path: "/dashboard",
    },
    {
      icon: Code2,
      label: "Code Review",
      path: "/review",
    },
    {
      icon: Languages,
      label: "Translation",
      path: "/translation",
    },
    {
      icon: FolderGit2,
      label: "Repository",
      path: "/repository",
    },
    {
      icon: History,
      label: "History",
      path: "/history",
    },
    {
      icon: Settings,
      label: "Settings",
      path: "/settings",
    },
  ];

  return (
    <aside className="w-64 h-screen bg-[#161A1F] border-r border-[#2F3541] flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-6 py-8 border-b border-[#2F3541]">
        <h1 className="text-3xl font-bold text-white">
          Kritiq
        </h1>

        <p className="text-xs uppercase tracking-[0.25em] text-[#8C909F] mt-2">
          AI Code Intelligence
        </p>
      </div>

      {/* Navigation */}
    <nav className="flex-1 px-4 py-6 space-y-1">
        {menuItems.map(({ icon: Icon, label, path }) => (
          <NavLink
            key={label}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-all ${
                isActive
                  ? "bg-[#1F3C68] text-[#ADC6FF]"
                  : "text-[#AEB5C9] hover:bg-[#232831] hover:text-white"
              }`
            }
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="border-t border-[#2F3541] p-4 space-y-1">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-[#AEB5C9] hover:bg-[#232831] hover:text-white transition">
          <UserCircle2 size={22} />
          Profile
        </button>

        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-[#AEB5C9] hover:bg-[#232831] hover:text-white transition">
          <CircleHelp size={22} />
          Support
        </button>
      </div>
    </aside>
  );
}
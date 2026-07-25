import { Bell, Search } from "lucide-react";

export default function NavBar() {
  return (
    <header className="h-20 bg-[#161A1F] border-b border-[#2F3541] flex items-center justify-between px-8">
      <div />

      <div className="flex items-center gap-4">
        <div className="flex items-center w-80 px-4 py-2.5 bg-[#1C2025] border border-[#424754] rounded-lg">
          <Search
            size={18}
            className="text-[#8C909F]"
          />

          <input
            type="text"
            placeholder="Search repositories..."
            className="ml-3 w-full bg-transparent text-white outline-none placeholder:text-[#8C909F]"
          />
        </div>

        <button className="w-11 h-11 rounded-lg border border-[#424754] bg-[#1C2025] flex items-center justify-center hover:bg-[#262A30] transition">
          <Bell
            size={20}
            className="text-white"
          />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-full bg-[#ADC6FF] flex items-center justify-center font-semibold text-[#002E6A]">
            D
          </div>

          <div>
            <p className="text-white font-medium">
              Dev
            </p>

            <p className="text-sm text-[#8C909F]">
              Frontend Developer
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
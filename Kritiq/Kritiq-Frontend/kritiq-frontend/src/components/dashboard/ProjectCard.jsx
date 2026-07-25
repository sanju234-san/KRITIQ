import {
  FolderGit2,
  ArrowUpRight,
  Clock3,
} from "lucide-react";

export default function ProjectCard({
  name,
  language,
  lastReview,
}) {
  return (
    <div className="bg-[#1C2025] border border-[#424754] rounded-xl p-5 hover:border-[#ADC6FF]/60 transition-all cursor-pointer group">
      <div className="flex justify-between items-start mb-5">
        <div className="w-10 h-10 rounded bg-[#1E293B] border border-[#424754] flex items-center justify-center">
          <FolderGit2
            size={20}
            className="text-[#ADC6FF]"
          />
        </div>

        <span className="text-[11px] px-2 py-1 rounded bg-[#31353B] text-[#C2C6D6]">
          {language}
        </span>
      </div>

      <h3 className="text-white text-lg font-semibold group-hover:text-[#ADC6FF] transition-colors">
        {name}
      </h3>

      <div className="flex items-center gap-2 mt-3 text-[#AEB5C9]">
        <Clock3 size={14} />

        <span className="text-sm">
          {lastReview}
        </span>
      </div>

      <ArrowUpRight
        size={18}
        className="absolute opacity-0"
      />
    </div>
  );
}
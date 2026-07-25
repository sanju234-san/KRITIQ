import { CloudUpload } from "lucide-react";

export default function QuickReview() {
  return (
    <section className="mt-6">
      <h3 className="text-xs font-bold uppercase tracking-widest text-[#8C909F] mb-4">
        Quick Review
      </h3>

      <div className="bg-[#181C21] border-2 border-dashed border-[#424754] rounded-xl p-10 flex flex-col items-center text-center hover:border-[#ADC6FF] hover:bg-[#1F3C68]/10 transition-all cursor-pointer group">
        <div className="w-16 h-16 rounded-full bg-[#ADC6FF]/10 flex items-center justify-center mb-5 group-hover:bg-[#ADC6FF]/20">
          <CloudUpload
            size={34}
            className="text-[#ADC6FF]"
          />
        </div>

        <h4 className="text-xl font-semibold text-white mb-2">
          Instant Analysis
        </h4>

        <p className="text-[#AEB5C9] mb-6">
          Drag &amp; drop files or{" "}
          <span className="text-[#ADC6FF] font-semibold">
            browse
          </span>{" "}
          to start a quick review
        </p>

        <div className="w-full flex flex-col gap-3">
          <button className="w-full py-3 bg-[#ADC6FF] text-[#002E6A] rounded-lg font-semibold hover:opacity-90 transition">
            Upload Files
          </button>

          <button className="w-full py-3 bg-[#1C2025] border border-[#424754] rounded-lg text-white font-semibold hover:bg-[#262A30] transition">
            Paste Code Block
          </button>
        </div>
      </div>
    </section>
  );
}
import { ArrowUpRight } from "lucide-react";

const FeatureCard = ({
  icon: Icon,
  title,
  description,
  accent = "violet",
}) => {
  const accentStyles = {
    violet: {
      iconBg: "bg-violet-500/10",
      iconColor: "text-violet-400",
      border: "group-hover:border-violet-500/40",
      glow: "group-hover:shadow-violet-500/10",
    },
    cyan: {
      iconBg: "bg-cyan-500/10",
      iconColor: "text-cyan-400",
      border: "group-hover:border-cyan-500/40",
      glow: "group-hover:shadow-cyan-500/10",
    },
    emerald: {
      iconBg: "bg-emerald-500/10",
      iconColor: "text-emerald-400",
      border: "group-hover:border-emerald-500/40",
      glow: "group-hover:shadow-emerald-500/10",
    },
    amber: {
      iconBg: "bg-amber-500/10",
      iconColor: "text-amber-400",
      border: "group-hover:border-amber-500/40",
      glow: "group-hover:shadow-amber-500/10",
    },
    pink: {
      iconBg: "bg-pink-500/10",
      iconColor: "text-pink-400",
      border: "group-hover:border-pink-500/40",
      glow: "group-hover:shadow-pink-500/10",
    },
    blue: {
      iconBg: "bg-blue-500/10",
      iconColor: "text-blue-400",
      border: "group-hover:border-blue-500/40",
      glow: "group-hover:shadow-blue-500/10",
    },
  };

  const style = accentStyles[accent];

  return (
    <div
      className={`group rounded-3xl border border-white/10 bg-white/[0.03] p-7 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 ${style.border} hover:shadow-2xl ${style.glow}`}
    >
      {/* Icon */}
      <div
        className={`mb-6 inline-flex rounded-2xl ${style.iconBg} p-4`}
      >
        <Icon
          size={28}
          className={`${style.iconColor} transition-transform duration-300 group-hover:scale-110`}
        />
      </div>

      {/* Title */}
      <h3 className="text-xl font-semibold text-white">
        {title}
      </h3>

      {/* Description */}
      <p className="mt-4 leading-7 text-gray-400">
        {description}
      </p>

      {/* Learn More */}
      <div className="mt-8 flex items-center gap-2 font-medium text-white opacity-0 transition-all duration-300 group-hover:translate-x-1 group-hover:opacity-100">
        Learn More
        <ArrowUpRight size={18} />
      </div>
    </div>
  );
};

export default FeatureCard;
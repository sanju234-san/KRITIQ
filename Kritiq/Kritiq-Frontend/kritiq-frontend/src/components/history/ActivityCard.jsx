import {
  CheckCircle2,
  Clock3,
  FolderSync,
  Languages,
  ShieldCheck,
  XCircle,
} from "lucide-react";

const ActivityCard = ({ activity }) => {
  const getIcon = () => {
    switch (activity.type) {
      case "review":
        return <ShieldCheck size={22} className="text-[#AFC8FF]" />;

      case "translation":
        return <Languages size={22} className="text-[#AFC8FF]" />;

      case "repository":
        return <FolderSync size={22} className="text-[#FCA5A5]" />;

      default:
        return <ShieldCheck size={22} className="text-[#AFC8FF]" />;
    }
  };

  const getStatus = () => {
    switch (activity.status) {
      case "success":
        return (
          <span className="flex items-center gap-2 text-green-400">
            <CheckCircle2 size={14} />
            Success
          </span>
        );

      case "running":
        return (
          <span className="flex items-center gap-2 text-[#AFC8FF]">
            <Clock3 size={14} />
            Running
          </span>
        );

      case "failed":
        return (
          <span className="flex items-center gap-2 text-red-400">
            <XCircle size={14} />
            Failed
          </span>
        );

      default:
        return null;
    }
  };

  return (
    <div className="rounded-2xl border border-[#34383d] bg-[#171F2D] p-6 transition-all duration-300 hover:border-[#AFC8FF]/40">
      <div className="flex gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#232A36]">
          {getIcon()}
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">
                {activity.title}
              </h3>

              <p className="mt-2 text-sm leading-6 text-[#A8AFBC]">
                {activity.description}
              </p>
            </div>

            {getStatus()}
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-6 text-sm text-[#8C909F]">
            <span>🕒 {activity.time}</span>

            {activity.ago && <span>{activity.ago}</span>}

            <span className="font-mono">{activity.ticket}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityCard;
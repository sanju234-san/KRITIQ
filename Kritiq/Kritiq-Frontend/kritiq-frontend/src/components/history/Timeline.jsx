import ActivityCard from "./ActivityCard";

const Timeline = ({ history }) => {
  const groupedHistory = history.reduce((acc, item) => {
    if (!acc[item.day]) acc[item.day] = [];
    acc[item.day].push(item);
    return acc;
  }, {});

  return (
    <div className="relative">
      {/* Vertical Line */}
      <div className="absolute left-5 top-0 bottom-0 w-px bg-[#34383d]" />

      {Object.entries(groupedHistory).map(([day, activities]) => (
        <div key={day} className="relative mb-10">
          {/* Timeline Dot */}
          <div className="absolute left-0 top-1 flex h-10 w-10 items-center justify-center rounded-full border border-[#4A5261] bg-[#171F2D]">
            <div className="h-3 w-3 rounded-full bg-[#AFC8FF]" />
          </div>

          {/* Day Label */}
          <div className="ml-16 mb-6">
            <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-white">
              {day}
            </h2>
          </div>

          {/* Activities */}
          <div className="ml-16 space-y-5">
            {activities.map((activity) => (
              <ActivityCard
                key={activity.id}
                activity={activity}
              />
            ))}
          </div>
        </div>
      ))}

      {/* Load More */}
      <div className="mt-12 flex justify-center">
        <button className="rounded-xl border border-[#34383d] bg-[#171F2D] px-8 py-3 text-sm font-semibold text-white transition hover:border-[#AFC8FF] hover:bg-[#1E2633]">
          Load Older Activities
        </button>
      </div>
    </div>
  );
};

export default Timeline;
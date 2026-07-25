import ReviewItem from "./ReviewItem";

const reviews = [
  {
    title: "Potential SQL Injection",
    severity: "Critical",
    time: "2 min ago",
  },
  {
    title: "Unused Variables",
    severity: "Medium",
    time: "15 min ago",
  },
  {
    title: "Missing Error Handling",
    severity: "High",
    time: "1 hour ago",
  },
  {
    title: "Code Formatting",
    severity: "Low",
    time: "Yesterday",
  },
];

export default function RecentReviews() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#8C909F]">
          Recent Reviews
        </h3>

        <button className="text-sm text-[#ADC6FF] hover:underline">
          View all
        </button>
      </div>

      <div className="bg-[#1C2025] border border-[#424754] rounded-xl p-5">
        {reviews.map((review, index) => (
          <ReviewItem
            key={index}
            {...review}
          />
        ))}
      </div>
    </section>
  );
}
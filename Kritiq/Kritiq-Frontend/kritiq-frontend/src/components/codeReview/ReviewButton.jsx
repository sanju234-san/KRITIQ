export default function ReviewButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700"
    >
      Review Code
    </button>
  );
}
export default function AuthCard({ title, subtitle, children }) {
  return (
    <section className="w-full rounded-2xl border border-white/10 bg-[rgba(19,21,26,0.8)] p-8 backdrop-blur-md md:p-10">
      <div className="mb-8">
        <h2 className="mb-2 text-2xl font-semibold text-white">
          {title}
        </h2>

        <p className="text-sm text-gray-400">
          {subtitle}
        </p>
      </div>

      {children}
    </section>
  );
}

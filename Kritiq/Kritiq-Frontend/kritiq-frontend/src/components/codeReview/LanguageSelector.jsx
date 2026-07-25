export default function LanguageSelector({
  language,
  setLanguage,
}) {
  return (
    <div className="mb-4 flex items-center justify-between">
      <label className="font-medium text-white">
        Language
      </label>

      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="rounded-lg border border-[#2A2F3A] bg-[#20242D] px-4 py-2 text-white outline-none focus:border-blue-500"
      >
        <option>Python</option>
        <option>JavaScript</option>
        <option>Java</option>
        <option>C++</option>
      </select>
    </div>
  );
}
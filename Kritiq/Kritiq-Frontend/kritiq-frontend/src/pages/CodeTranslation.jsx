import TranslationCard from "../components/translation/TranslationCard";

export default function CodeTranslation() {
  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8C909F] mb-2">
          AI Translation
        </p>

        <h1 className="text-4xl font-bold text-white">
          Translate Code
        </h1>

        <p className="mt-3 text-[#AEB5C9] max-w-3xl">
          Translate your source code across programming languages while
          preserving logic, readability, and architecture using Kritiq AI.
        </p>
      </div>

      <TranslationCard />
    </div>
  );
}
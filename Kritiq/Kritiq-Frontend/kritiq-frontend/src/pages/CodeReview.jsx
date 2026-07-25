import CodeInputCard from "../components/codeReview/CodeInputCard";

export default function CodeReview() {
  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8C909F] mb-2">
          AI Review
        </p>

        <h1 className="text-4xl font-bold text-white">
          Code Review
        </h1>

        <p className="mt-3 text-[#AEB5C9] max-w-3xl">
          Paste your source code below and let Kritiq analyze
          security vulnerabilities, code quality, performance,
          maintainability, and best practices using AI.
        </p>
      </div>

      <CodeInputCard />
    </div>
  );
}
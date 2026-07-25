import { useState } from "react";
import {
  ArrowLeftRight,
  Copy,
  Download,
  Loader2,
  RefreshCw,
  FileCode2,
  FileJson2,
  MoreHorizontal,
  Sparkles,
  Cog,
  ShieldCheck,
  LayoutTemplate,
} from "lucide-react";

import { translateCode } from "../../api/translationApi";

const LANGUAGES = [
  "Python",
  "Java",
  "JavaScript",
  "TypeScript",
  "C",
  "C++",
  "C#",
  "Go",
  "Rust",
  "PHP",
  "Swift",
  "Kotlin",
];

const EXT_MAP = {
  Python: "py",
  Java: "java",
  JavaScript: "js",
  TypeScript: "ts",
  C: "c",
  "C++": "cpp",
  "C#": "cs",
  Go: "go",
  Rust: "rs",
  PHP: "php",
  Swift: "swift",
  Kotlin: "kt",
};

export default function TranslationCard() {
  const [sourceLanguage, setSourceLanguage] = useState("Python");
  const [targetLanguage, setTargetLanguage] = useState("TypeScript");

  const [sourceCode, setSourceCode] = useState(`def calculate_growth_rate(initial, current, time_period):
    """
    Calculates the exponential growth rate over a set period.
    """
    if time_period <= 0:
        return 0

    growth_multiplier = current / initial
    rate = (growth_multiplier ** (1 / time_period)) - 1

    return round(rate, 4)`);

  const [translatedCode, setTranslatedCode] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [compareMode, setCompareMode] = useState(false);

  const handleTranslate = async () => {
    if (!sourceCode.trim()) return;

    try {
      setError("");
      setLoading(true);

      const res = await translateCode({
        source_code: sourceCode,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      });

      setTranslatedCode(res.data.translated_code ?? "");
      setNotes(res.data.notes ?? "");
    } catch (err) {
      console.error(err);
      setError("Translation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
    setSourceCode(translatedCode);
    setTranslatedCode(sourceCode);
  };

  const copyOutput = async () => {
    if (!translatedCode) return;
    await navigator.clipboard.writeText(translatedCode);
  };

  const downloadOutput = () => {
    if (!translatedCode) return;

    const blob = new Blob([translatedCode], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = `translated.${targetLanguage.toLowerCase()}`;
    a.click();

    URL.revokeObjectURL(url);
  };

  const sourceLines = Array.from(
    { length: Math.max(sourceCode.split("\n").length, 14) },
    (_, i) => i + 1
  );

  return (
    <div className="space-y-6">
  {/* Controls row — no title here, the page header already shows it */}
  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

    <div className="flex flex-wrap items-center gap-3">

      {/* Compare Toggle */}

      <div className="flex items-center gap-3 rounded-xl border border-[#34383d] bg-[#111418] px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#8C909F]">
            Compare Differences
        </span>

        <button
            type="button"
            onClick={() => setCompareMode(!compareMode)}
            className={`relative h-8 w-16 rounded-full border-2 border-white transition-all duration-300 ${
            compareMode ? "bg-blue-500" : "bg-[#34383d]"
            }`}
        >
            <span
            className={`absolute top-[2px] h-6 w-6 rounded-full bg-white shadow-md transition-all duration-300 ${
                compareMode ? "left-[34px]" : "left-[2px]"
            }`}
            />
        </button>
        </div>

      {/* Language Selector */}

      <div className="flex items-center gap-2 rounded-xl border border-[#34383d] bg-[#111418] px-3 py-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#8C909F]">
          From
        </span>

        <select
          value={sourceLanguage}
          onChange={(e) => setSourceLanguage(e.target.value)}
          className="bg-transparent text-sm text-white outline-none"
        >
          {LANGUAGES.map((lang) => (
            <option key={lang} className="bg-[#111418]">
              {lang}
            </option>
          ))}
        </select>

        <button
          onClick={handleSwap}
          className="rounded-lg p-1.5 text-gray-400 transition hover:text-blue-400"
        >
          <ArrowLeftRight size={16} />
        </button>

        <span className="text-xs font-semibold uppercase tracking-wider text-[#8C909F]">
          To
        </span>

        <select
          value={targetLanguage}
          onChange={(e) => setTargetLanguage(e.target.value)}
          className="bg-transparent text-sm text-white outline-none"
        >
          {LANGUAGES.map((lang) => (
            <option key={lang} className="bg-[#111418]">
              {lang}
            </option>
          ))}
        </select>
      </div>

    </div>

<button
  onClick={handleTranslate}
  disabled={loading || !sourceCode.trim()}
  className="flex items-center justify-center gap-2 rounded-lg bg-blue-200 px-4 py-2 text-blue-950 hover:bg-blue-300"
>
  {loading ? (
    <>
      <Loader2 size={16} className="animate-spin" />
      Translating...
    </>
  ) : (
    <>
      <RefreshCw size={16} />
      Translate Code
    </>
  )}
</button>

  </div>

    {error && (
    <p className="text-sm text-red-400">
        {error}
    </p>
    )}

      {/* Merged editor card */}
      <div className="overflow-hidden rounded-2xl border border-[#34383d] bg-[#080a0d]">
        <div className="grid grid-cols-1 divide-y divide-[#34383d] lg:grid-cols-2 lg:divide-x lg:divide-y-0">
          {/* Source pane */}
          <div>
            <div className="flex h-11 items-center justify-between border-b border-[#34383d] bg-[#111418] px-4">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <FileCode2 size={16} className="text-blue-400" />
                source_snippet.{EXT_MAP[sourceLanguage] || "txt"}
              </div>
              <MoreHorizontal size={18} className="text-gray-500" />
            </div>

            <div className="flex h-[480px]">
              <div className="w-14 select-none overflow-hidden border-r border-[#34383d] bg-[#111418] py-4 text-center text-xs text-gray-500">
                {sourceLines.map((line) => (
                  <div key={line} className="h-6 leading-6">
                    {line}
                  </div>
                ))}
              </div>
              <textarea
                value={sourceCode}
                spellCheck={false}
                onChange={(e) => setSourceCode(e.target.value)}
                placeholder="Paste your source code..."
                className="flex-1 resize-none bg-transparent p-4 font-mono text-sm leading-6 text-white outline-none"
              />
            </div>
          </div>

          {/* Output pane */}
          <div>
            <div className="flex items-center justify-between border-b border-[#34383d] bg-[#111418] px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <FileJson2 size={16} className="text-orange-400" />
                output_module.{EXT_MAP[targetLanguage] || "txt"}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={copyOutput}
                  className="rounded-lg border border-[#34383d] p-2 text-gray-400 transition hover:text-blue-400"
                >
                  <Copy size={16} />
                </button>
                <button
                  onClick={downloadOutput}
                  className="rounded-lg border border-[#34383d] p-2 text-gray-400 transition hover:text-blue-400"
                >
                  <Download size={16} />
                </button>
              </div>
            </div>

            <div className="relative h-[480px] overflow-auto">
              {!translatedCode && !loading && (
                <div className="absolute inset-0 flex flex-col items-center justify-center px-6">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#1a1d23]">
                    <Sparkles size={22} className="text-gray-400" />
                  </div>
                  <p className="text-center text-sm text-gray-400">
                    Click translate to generate
                    <br />
                    type-safe code
                  </p>
                </div>
              )}

              {loading && (
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <Loader2 size={40} className="mb-4 animate-spin text-blue-500" />
                  <h3 className="text-lg font-semibold text-white">Translating...</h3>
                  <p className="mt-2 text-sm text-gray-500">Kritiq AI is generating your code.</p>
                </div>
              )}

              {translatedCode && (
                <pre className="h-full overflow-auto p-4 font-mono text-sm leading-6 text-white">
                  {translatedCode}
                </pre>
              )}

              {notes && (
                <div className="border-t border-[#34383d] p-4">
                  <p className="mb-1 text-xs uppercase text-gray-500">Translation Notes</p>
                  <p className="text-sm text-gray-300">{notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-[#34383d] bg-[#111418] p-5">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[#1a1d23]">
            <Cog size={20} className="text-gray-300" />
          </div>
          <h3 className="mb-2 font-semibold text-white">Pattern Matching</h3>
          <p className="text-sm text-gray-400">
            AI analyzes idiomatic patterns to ensure the output feels native to the target ecosystem.
          </p>
        </div>

        <div className="rounded-2xl border border-[#34383d] bg-[#111418] p-5">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[#1a1d23]">
            <ShieldCheck size={20} className="text-gray-300" />
          </div>
          <h3 className="mb-2 font-semibold text-white">Type Inference</h3>
          <p className="text-sm text-gray-400">
            Automatically maps Python's duck typing to strict TypeScript interfaces and generics.
          </p>
        </div>

        <div className="rounded-2xl border border-[#34383d] bg-[#111418] p-5">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[#1a1d23]">
            <LayoutTemplate size={20} className="text-gray-300" />
          </div>
          <h3 className="mb-2 font-semibold text-white">Architecture Aware</h3>
          <p className="text-sm text-gray-400">
            Maintains functional purity and class structures during the transpilation process.
          </p>
        </div>
      </div>
    </div>
  );
}

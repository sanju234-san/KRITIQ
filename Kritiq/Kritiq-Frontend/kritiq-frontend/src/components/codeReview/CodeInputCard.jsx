import { useState } from "react";
import LanguageSelector from "./LanguageSelector";
import ReviewButton from "./ReviewButton";
import { reviewCode } from "../../api/reviewApi";

export default function CodeInputCard() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [loading, setLoading] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);

  const handleReview = async () => {
    if (!code.trim()) {
      alert("Please enter some code.");
      return;
    }

    try {
      setLoading(true);

      const response = await reviewCode({
        code,
        language: language.toLowerCase(),
        filename: "main.py",
        repo_url: "",
      });

      setReviewResult(response.data);
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Failed to review code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="mt-8 rounded-xl border border-[#2A2F3A] bg-[#171B22] p-6">
        <LanguageSelector
          language={language}
          setLanguage={setLanguage}
        />

        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste your code here..."
          className="mt-4 h-80 w-full rounded-lg border border-[#2A2F3A] bg-[#101419] p-4 text-white outline-none resize-none focus:border-[#ADC6FF]"
        />

        <div className="mt-4 flex justify-between text-sm text-gray-400">
          <span>Characters: {code.length}</span>
          <span>{language}</span>
        </div>

        <div className="mt-6 flex justify-end">
          <ReviewButton
            onClick={handleReview}
            disabled={loading}
          >
            {loading ? "Reviewing..." : "Run AI Review"}
          </ReviewButton>
        </div>
      </div>

      {reviewResult && (
        <div className="mt-8 rounded-xl border border-[#2A2F3A] bg-[#171B22] p-6">
          <h2 className="text-2xl font-semibold text-white mb-4">
            AI Review Result
          </h2>

          <div className="mb-6">
            <h3 className="text-[#ADC6FF] font-semibold mb-2">
              Summary
            </h3>

            <p className="text-gray-300">
              {reviewResult.summary}
            </p>
          </div>

          <div>
            <h3 className="text-[#ADC6FF] font-semibold mb-4">
              Issues Found
            </h3>

            {reviewResult.issues?.length > 0 ? (
              <div className="space-y-4">
                {reviewResult.issues.map((issue, index) => (
                  <div
                    key={index}
                    className="rounded-lg border border-[#2A2F3A] bg-[#101419] p-5"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-semibold text-white">
                        {issue.title}
                      </h4>

                      <span className="rounded-md bg-red-500/20 px-3 py-1 text-sm text-red-400 capitalize">
                        {issue.severity}
                      </span>
                    </div>

                    <p className="mt-3 text-gray-300">
                      {issue.explanation}
                    </p>

                    <div className="mt-4 rounded-lg bg-[#171B22] p-4 border border-[#2A2F3A]">
                      <p className="text-[#ADC6FF] font-medium mb-2">
                        Suggested Fix
                      </p>

                      <p className="text-gray-300">
                        {issue.suggested_fix}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-green-400">
                🎉 No issues found.
              </p>
            )}
          </div>
        </div>
      )}
    </>
  );
}
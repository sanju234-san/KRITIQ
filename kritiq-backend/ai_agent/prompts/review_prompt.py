def build_review_prompt(code: str, language: str = "python", retrieved_examples: list[dict] = None, project_context: list[str] = None) -> str:
    reference_section = ""
    if retrieved_examples:
        reference_section = "\nReference Examples of Bad Practices:\n"
        for idx, example in enumerate(retrieved_examples):
            reference_section += f"\nExample {idx + 1}:\n"
            reference_section += f"Code Snippet:\n{example.get('code_snippet', '')}\n"
            reference_section += f"Explanation: {example.get('explanation', '')}\n"
            reference_section += "-" * 40 + "\n"

    context_section = ""
    if project_context:
        file_list = ", ".join(project_context)
        context_section = f"""
Project Context:
This file exists alongside these other files in the same project directory: {file_list}.
Consider whether this code might duplicate logic or violate conventions used elsewhere in the project, if relevant.
"""

    return f"""
You are a principal software engineer and security auditor performing a comprehensive code review.
Review the following {language} code and identify actionable bugs, security vulnerabilities, edge cases, performance bottlenecks, and structural code smells. Avoid trivial formatting nitpicks.

IMPORTANT: Return ONLY valid JSON. Do not return Markdown, headings, bullet points, prose, or code fences outside the JSON object.

The JSON MUST have exactly this top-level shape:
{{
  "summary": "1-2 sentence overview of the code's overall quality and risk profile",
  "issues": [
    {{
      "title": "Short descriptive issue title",
      "line": 12,
      "severity": "medium",
      "explanation": "Detailed root cause and impact",
      "suggested_fix": "Concrete production-ready fix or code change"
    }}
  ]
}}

Rules:
- "summary" must be a string.
- "issues" must be an array. Use [] when there are no actionable issues.
- "title" must be a short plain-text title. Do not include Markdown emphasis.
- "line" must be an integer for the most relevant source line, or null when no specific line applies.
- "severity" must be exactly one of: "high", "medium", "low".
- "explanation" must be a clear explanation. Markdown is allowed inside this string if useful, but do not put Markdown around the JSON structure.
- "suggested_fix" must be a string or null.
- Never concatenate fields together. Keep title, line, severity, explanation, and suggested_fix as separate JSON properties.
- Never write labels such as "Summary:", "Issues:", "Explanation:", or "Suggested Fix:" outside their JSON properties.
- Do not invent line numbers. Use null when uncertain.
{reference_section}{context_section}
Code:
{code}
""".strip()

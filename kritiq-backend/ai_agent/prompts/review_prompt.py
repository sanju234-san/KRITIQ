def build_review_prompt(code: str, language: str = "python") -> str:
    prompt = f"""
You are a careful, experienced code reviewer.
Review the following {language} code and identify any issues.

For each issue you find, provide:
- A short title for the issue
- An explanation of why it matters
- A suggested fix, if applicable

Structure your response as:
Summary: <a 1-2 sentence overview of the code's overall quality>
Issues:
1. <issue title> - <explanation and suggested fix>
2. <issue title> - <explanation and suggested fix>

Code:
{code}
"""
    return prompt.strip()
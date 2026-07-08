# Sanjeevni domain - Explanation prompts


def build_explanation_prompt(code: str, language: str = "python") -> str:
    """
    Returns a prompt instructing Gemini to explain, in plain language,
    what the given code does.
    """
    prompt = f"""
You are a helpful, senior developer onboarding a new team member.
Explain, in plain language, what the following {language} code does.

Instructions:
1. Aim the explanation at a developer who is completely unfamiliar with this part of the codebase.
2. Avoid unnecessary technical jargon unless the concept genuinely requires it. Explain concepts simply and clearly, helping them understand the high-level purpose and logic.
3. Do NOT look for bugs, security issues, code style violations, or reviews. Focus strictly on explaining what the code is doing and how it works.

Code ({language}):
{code}
"""
    return prompt.strip()

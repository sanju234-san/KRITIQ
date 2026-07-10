# Sanjeevni domain - Explanation prompts


def build_explanation_prompt(code: str, language: str = "python", retrieved_examples: list[dict] = None, project_context: list[str] = None) -> str:
    """
    Returns a prompt instructing Gemini to explain, in plain language,
    what the given code does.
    """
    reference_section = ""
    if retrieved_examples:
        reference_section = "\nReference Examples of Code Context/Explanations:\n"
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
Consider how this code fits into the surrounding project files, or if it interacts with them, when explaining its role.
"""

    prompt = f"""
You are a helpful, senior developer onboarding a new team member.
Explain, in plain language, what the following {language} code does.

Instructions:
1. Aim the explanation at a developer who is completely unfamiliar with this part of the codebase.
2. Avoid unnecessary technical jargon unless the concept genuinely requires it. Explain concepts simply and clearly, helping them understand the high-level purpose and logic.
3. Do NOT look for bugs, security issues, code style violations, or reviews. Focus strictly on explaining what the code is doing and how it works.
{reference_section}{context_section}
Code ({language}):
{code}
"""
    return prompt.strip()


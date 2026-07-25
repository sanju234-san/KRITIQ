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

    prompt = f"""
You are a careful, experienced code reviewer.
Review the following {language} code and identify any issues.

For each issue you find, provide:
- A short title for the issue
- An explanation of why it matters
- A suggested fix, if applicable
{reference_section}{context_section}
Structure your response as:
Summary: <a 1-2 sentence overview of the code's overall quality>
Issues:
1. <issue title> - <explanation and suggested fix>
2. <issue title> - <explanation and suggested fix>

Code:
{code}
"""
    return prompt.strip()
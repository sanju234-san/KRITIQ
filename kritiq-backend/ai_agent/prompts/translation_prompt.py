# Sanjeevni domain - Translation prompts


def build_translation_prompt(code: str, source_language: str, target_language: str, retrieved_examples: list[dict] = None, project_context: list[str] = None) -> str:
    """
    Returns a prompt string instructing Gemini to translate the given code
    from source_language to target_language.
    """
    reference_section = ""
    if retrieved_examples:
        reference_section = "\nReference Examples of Common Issues:\n"
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
Consider whether naming conventions, import patterns, or architectural styles from sibling files should be preserved in the translation, if relevant.
"""

    prompt = f"""
You are an expert polyglot programmer.
Translate the following code from {source_language} to {target_language}.

Instructions:
1. Preserve the original logic, structure, and behavior of the code. Do not just produce syntactically valid code; ensure that it computes the exact same results.
2. Return ONLY the translated code.
3. Do not include any explanations, markdown code blocks (e.g. ```), metadata, comments, or introductory/concluding commentary. The output must be ready to write directly to a file.
4. Return the code as a single block of raw code.
{reference_section}{context_section}
Source Code ({source_language}):
{code}
"""
    return prompt.strip()


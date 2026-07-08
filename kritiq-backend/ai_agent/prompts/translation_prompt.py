# Sanjeevni domain - Translation prompts


def build_translation_prompt(code: str, source_language: str, target_language: str) -> str:
    """
    Returns a prompt string instructing Gemini to translate the given code
    from source_language to target_language.
    """
    prompt = f"""
You are an expert polyglot programmer.
Translate the following code from {source_language} to {target_language}.

Instructions:
1. Preserve the original logic, structure, and behavior of the code. Do not just produce syntactically valid code; ensure that it computes the exact same results.
2. Return ONLY the translated code.
3. Do not include any explanations, markdown code blocks (e.g. ```), metadata, comments, or introductory/concluding commentary. The output must be ready to write directly to a file.
4. Return the code as a single block of raw code.

Source Code ({source_language}):
{code}
"""
    return prompt.strip()

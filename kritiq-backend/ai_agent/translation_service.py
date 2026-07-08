from ai_agent.prompts.translation_prompt import build_translation_prompt
from ai_agent.gemini_client import ask_gemini


def translate_code(code: str, source_language: str, target_language: str) -> str:
    """
    Calls build_translation_prompt, passes the result to ask_gemini,
    and returns the raw text response.
    """
    prompt = build_translation_prompt(code, source_language, target_language)
    return ask_gemini(prompt)

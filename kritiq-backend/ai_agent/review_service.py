from ai_agent.prompts.review_prompt import build_review_prompt
from ai_agent.gemini_client import ask_gemini


def review_code(code: str, language: str = "python") -> str:
    """
    Builds a review prompt and calls Gemini to review the provided code.
    """
    prompt = build_review_prompt(code, language)
    return ask_gemini(prompt)

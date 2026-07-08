from ai_agent.prompts.explanation_prompt import build_explanation_prompt
from ai_agent.gemini_client import ask_gemini


def explain_code(code: str, language: str = "python") -> str:
    """
    Calls build_explanation_prompt, passes the result to ask_gemini,
    and returns the raw text response.
    """
    prompt = build_explanation_prompt(code, language)
    return ask_gemini(prompt)

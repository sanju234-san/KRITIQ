from ai_agent.gemini_client import ask_gemini
from ai_agent.groq_client import ask_groq
from ai_agent.prompts.multi_agent_prompts import build_reviewer_prompt, build_verifier_prompt


def multi_agent_review(code: str, language: str = "python") -> str:
    """
    Runs a two-agent code review workflow:
    1. Agent 1 (Reviewer - Gemini) identifies potential issues in the code.
    2. Agent 2 (Verifier - Groq) verifies these issues against the original code
       and returns only the confirmed issues.

    Note: This process executes 1 Gemini API call and 1 Groq API call.
    """
    print(f"\n--- Initiating Multi-Agent Code Review ({language}) ---")
    print("[Agent 1] Reviewer (Gemini) is analyzing the code...")

    # 1. Generate prompt for Agent 1 (Reviewer) and call Gemini
    reviewer_prompt = build_reviewer_prompt(code, language)
    reviewer_issues = ask_gemini(reviewer_prompt)

    print("\n[Agent 1] Reviewer findings:")
    print(reviewer_issues)

    print("\n[Agent 2] Verifier (Groq) is checking the findings...")

    # 2. Generate prompt for Agent 2 (Verifier) and call Groq
    verifier_prompt = build_verifier_prompt(code, language, reviewer_issues)
    verified_issues = ask_groq(verifier_prompt)

    print("--- Multi-Agent Code Review Finished ---\n")
    return verified_issues


if __name__ == "__main__":
    # Test sample code snippet containing obvious bugs (missing return, unused variable)
    SAMPLE_CODE = """\
def calculate_discount(price, discount_percent):
    unused_var = "debug"
    discount_amount = price * discount_percent / 100
    discounted = price - discount_amount
    # missing return statement
"""
    print("Testing multi_agent_review with a hardcoded sample snippet...")
    result = multi_agent_review(SAMPLE_CODE, "python")
    print("=" * 60)
    print("FINAL VERIFIED ISSUES:")
    print("=" * 60)
    print(result)

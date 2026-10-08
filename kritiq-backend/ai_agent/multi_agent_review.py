from ai_agent.gemini_client import ask_gemini
from ai_agent.groq_client import ask_groq
from ai_agent.prompts.multi_agent_prompts import (
    build_reviewer_prompt,
    build_verifier_prompt
)


def multi_agent_review(
    code: str,
    language: str = "python"
) -> str:
    """
    Runs a two-agent code review workflow:

    1. Agent 1 (Reviewer - Gemini) identifies potential issues.
    2. Agent 2 (Verifier - Groq) verifies those issues against
       the original code and returns only confirmed issues.

    Both agents explicitly use JSON response mode because the
    multi-agent review expects structured review output.
    """

    print(
        f"\n--- Initiating Multi-Agent Code Review ({language}) ---"
    )

    # ---------------------------------------------------------
    # Agent 1: Gemini Reviewer
    # ---------------------------------------------------------
    print(
        "[Agent 1] Reviewer (Gemini) is analyzing the code..."
    )

    reviewer_prompt = build_reviewer_prompt(
        code,
        language
    )

    # IMPORTANT:
    # Multi-agent review requires JSON.
    reviewer_issues = ask_gemini(
        reviewer_prompt,
        "json"
    )

    print("\n[Agent 1] Reviewer findings:")
    print(reviewer_issues)

    # ---------------------------------------------------------
    # Agent 2: Groq Verifier
    # ---------------------------------------------------------
    print(
        "\n[Agent 2] Verifier (Groq) is checking the findings..."
    )

    verifier_prompt = build_verifier_prompt(
        code,
        language,
        reviewer_issues
    )

    # IMPORTANT:
    # Multi-agent review also requires JSON.
    verified_issues = ask_groq(
        verifier_prompt,
        "json"
    )

    print(
        "--- Multi-Agent Code Review Finished ---\n"
    )

    return verified_issues


if __name__ == "__main__":
    SAMPLE_CODE = """\
def calculate_discount(price, discount_percent):
    unused_var = "debug"
    discount_amount = price * discount_percent / 100
    discounted = price - discount_amount
    # missing return statement
"""

    print(
        "Testing multi_agent_review with a hardcoded "
        "sample snippet..."
    )

    result = multi_agent_review(
        SAMPLE_CODE,
        "python"
    )

    print("=" * 60)
    print("FINAL VERIFIED ISSUES:")
    print("=" * 60)
    print(result)
"""
kritiq-backend/playground.py

Runs all major backend components in sequence to confirm nothing is broken
when used as a whole rather than in isolation.

Run with:
    python -m playground
"""

import time

# ─── Sample code used across review / explain / translate steps ───────────────
SAMPLE_CODE = """\
def calculate_discount(price, discount_percent):
    unused_var = "debug"
    discount_amount = price * discount_percent / 100
    discounted = price - discount_amount
    # missing return statement
"""

# ─── Helper ───────────────────────────────────────────────────────────────────

def run_step(step_number: int, label: str, fn, *args, **kwargs):
    """
    Runs a single step, prints its output and duration.
    Returns (success: bool, result_or_error).
    """
    print(f"\n{'='*60}")
    print(f"=== STEP {step_number}: {label} ===")
    print(f"{'='*60}")
    start = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
        duration = time.perf_counter() - start
        print(result)
        print(f"\n[Step {step_number} completed in {duration:.2f}s]")
        return True, result
    except Exception as e:
        duration = time.perf_counter() - start
        print(f"[FAILED] Step {step_number} — {label}")
        print(f"Error: {e}")
        print(f"[Step {step_number} failed after {duration:.2f}s]")
        return False, e


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    failures = []

    # ── Step 1: List local files ───────────────────────────────────────────────
    from mcp_server.tools import list_local_files

    ok, result = run_step(1, "List Local Files (.)", list_local_files, ".")
    if not ok:
        failures.append(1)

    # ── Step 2: List GitHub repo files ────────────────────────────────────────
    from repo_integration.github_api import list_repo_files

    ok, result = run_step(2, "List GitHub Repo Files (octocat/Hello-World)",
                          list_repo_files, "octocat", "Hello-World")
    if not ok:
        failures.append(2)

    # ── Step 3a: Review code ──────────────────────────────────────────────────
    from ai_agent.review_service import review_code

    print(f"\n{'='*60}")
    print(f"=== Sample code being used for steps 3a / 3b / 3c ===")
    print(f"{'='*60}")
    print(SAMPLE_CODE)

    ok, result = run_step(3, "Review Code (AI)", review_code,
                          SAMPLE_CODE, "python")
    if not ok:
        failures.append("3a")

    # ── Step 3b: Explain code ─────────────────────────────────────────────────
    from ai_agent.explanation_service import explain_code

    ok, result = run_step(4, "Explain Code (AI)", explain_code,
                          SAMPLE_CODE, "python")
    if not ok:
        failures.append("3b")

    # ── Step 3c: Translate code ───────────────────────────────────────────────
    from ai_agent.translation_service import translate_code

    ok, result = run_step(5, "Translate Code Python -> Java (AI)", translate_code,
                          SAMPLE_CODE, "python", "java")
    if not ok:
        failures.append("3c")

    # ── Final summary ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if failures:
        print(f"=== COMPLETED WITH FAILURES ===")
        print(f"Failed steps: {failures}")
    else:
        print(f"=== ALL STEPS COMPLETED SUCCESSFULLY ===")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

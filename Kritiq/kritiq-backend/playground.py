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
    total_start = time.perf_counter()

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
    print(f"=== Sample code being used for steps 3a / 3b / 3c / 4 / 6 ===")
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

    # ── Step 4: Review with MCP + RAG context (file_path) ─────────────────────
    ok, result = run_step(6, "Review Code with MCP + RAG context (file_path)", review_code,
                          SAMPLE_CODE, "python", "test_sample.py")
    if not ok:
        failures.append(4)

    # ── Step 5: Combined embeddings dataset count ─────────────────────────────
    def check_combined_embeddings():
        from rag_pipeline.retriever import get_or_build_combined_embeddings
        combined = get_or_build_combined_embeddings()
        count = len(combined)
        return f"Total entries loaded from combined dataset: {count} (expected 24)"

    ok, result = run_step(7, "Combined Embeddings Dataset Count", check_combined_embeddings)
    if not ok:
        failures.append(5)

    # ── Step 6: Multi-agent review (Gemini + Groq) ────────────────────────────
    from ai_agent.multi_agent_review import multi_agent_review

    ok, result = run_step(8, "Multi-Agent Review: Gemini (Reviewer) + Groq (Verifier)",
                          multi_agent_review, SAMPLE_CODE, "python")
    if not ok:
        failures.append(6)

    # ── STEP A: Test review_code() with file_path (costs 2 Gemini calls: embed + generate) ──
    from ai_agent.review_service import review_code
    ok_a, review_res = run_step(9, "STEP A: Review Code with file_path (MCP + RAG)", review_code,
                                 SAMPLE_CODE, "python", file_path="test_sample.py")
    if not ok_a:
        failures.append("A")

    # ── STEP B: Test translate_code() with file_path (costs 2 Gemini calls) ──
    from ai_agent.translation_service import translate_code
    ok_b, translate_res = run_step(10, "STEP B: Translate Code with file_path (MCP + RAG)", translate_code,
                                     SAMPLE_CODE, "python", "java", file_path="test_sample.py")
    if not ok_b:
        failures.append("B")

    # ── STEP C: Test explain_code() with file_path (costs 2 Gemini calls) ──
    from ai_agent.explanation_service import explain_code
    ok_c, explain_res = run_step(11, "STEP C: Explain Code with file_path (MCP + RAG)", explain_code,
                                   SAMPLE_CODE, "python", file_path="test_sample.py")
    if not ok_c:
        failures.append("C")

    # ── STEP D: Test walkthrough generation (ZERO additional API cost) ──
    def run_walkthrough_test(r_res, t_res):
        from ai_agent.walkthrough_writer import write_review_walkthrough, write_translation_walkthrough
        import os
        
        # Test Review Walkthrough
        try:
            review_path = write_review_walkthrough("test_sample.py", "python", r_res)
            review_exists = os.path.exists(review_path)
            print(f"Review Walkthrough File Existence: {'PASS' if review_exists else 'FAIL'} ({review_path})")
        except Exception as e:
            print(f"Review Walkthrough Failed: {e}")
            review_exists = False
            
        # Test Translation Walkthrough
        try:
            translation_path = write_translation_walkthrough("test_sample.py", "python", "java", t_res)
            translation_exists = os.path.exists(translation_path)
            print(f"Translation Walkthrough File Existence: {'PASS' if translation_exists else 'FAIL'} ({translation_path})")
        except Exception as e:
            print(f"Translation Walkthrough Failed: {e}")
            translation_exists = False
            
        return f"Review Walkthrough: {'PASS' if review_exists else 'FAIL'}, Translation Walkthrough: {'PASS' if translation_exists else 'FAIL'}"

    ok_d, walkthrough_res = run_step(12, "STEP D: Walkthrough File Generation", run_walkthrough_test,
                                     review_res if ok_a else "Mock review result",
                                     translate_res if ok_b else "Mock translation result")
    if not ok_d:
        failures.append("D")

    # ── STEP E: Test get_or_build_combined_embeddings() (ZERO API cost if cache already exists) ──
    def run_combined_embeddings_test():
        from rag_pipeline.retriever import get_or_build_combined_embeddings
        combined = get_or_build_combined_embeddings()
        count = len(combined)
        return f"Loaded {count} total entries from combined dataset (expecting 24)."

    ok_e, embeddings_res = run_step(13, "STEP E: Check Combined Embeddings", run_combined_embeddings_test)
    if not ok_e:
        failures.append("E")

    # ── Final summary ─────────────────────────────────────────────────────────
    total_duration = time.perf_counter() - total_start
    print(f"\n{'='*60}")
    if failures:
        print(f"=== COMPLETED WITH FAILURES ===")
        print(f"Failed steps: {failures}")
    else:
        print(f"=== ALL STEPS COMPLETED SUCCESSFULLY ===")
    print(f"{'='*60}")

    # ── API quota usage estimate ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"=== ESTIMATED API QUOTA USAGE ===")
    print(f"{'='*60}")
    print(f"  Step 3  (Review):         1 embed + 1 generate = 2 Gemini calls")
    print(f"  Step 4  (Explain):        1 generate            = 1 Gemini call")
    print(f"  Step 5  (Translate):      1 generate            = 1 Gemini call")
    print(f"  Step 6  (Review+MCP+RAG): 1 embed + 1 generate = 2 Gemini calls")
    print(f"  Step 7  (Embeddings):     0 calls (loaded from cache)")
    print(f"  Step 8  (Multi-Agent):    1 Gemini + 1 Groq     = 2 calls")
    print(f"  ---------------------------------------------------------")
    print(f"  NEW STEPS ADDED THIS RUN:")
    print(f"  STEP A  (Review+file_path): 1 embed + 1 generate = 2 Gemini calls")
    print(f"  STEP B  (Trans+file_path):  1 embed + 1 generate = 2 Gemini calls")
    print(f"  STEP C  (Explain+file_path): 1 embed + 1 generate = 2 Gemini calls")
    print(f"  STEP D  (Walkthrough):      0 calls (reformats existing outputs)")
    print(f"  STEP E  (Embeddings check): 0 calls (loaded from cache)")
    print(f"  ---------------------------------------------------------")
    print(f"  TOTAL ESTIMATED GEMINI CALLS: ~12 Gemini API calls + 1 Groq API call")
    print(f"  (Embedding cache reused across runs -- 0 extra embed calls if cache exists)")
    print(f"\n  Total runtime: {total_duration:.2f}s")
    print(f"{'='*60}\n")



if __name__ == "__main__":
    main()


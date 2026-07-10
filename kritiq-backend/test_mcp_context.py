"""
Test script for MCP context-gathering logic in review_service.py.
Verifies sibling file discovery and filtering WITHOUT calling any external APIs.
Zero Gemini/Groq/embedding calls — safe to run unlimited times.
"""
import os
from mcp_server.tools import list_local_files


def get_project_context(file_path: str) -> list[str] | None:
    """
    Extracted MCP context logic — identical to what review_service.py does,
    but without any RAG or Gemini calls.
    """
    project_context = None

    if file_path:
        try:
            directory = os.path.dirname(file_path) or "."
            sibling_files = list_local_files(directory)

            if sibling_files and not any(f.startswith("Error:") for f in sibling_files):
                basename = os.path.basename(file_path)
                project_context = [f for f in sibling_files if f != basename]
                if not project_context:
                    project_context = None
        except Exception as e:
            print(f"  [MCP WARNING] Exception: {e}")
            project_context = None

    return project_context


def run_test(label: str, file_path: str):
    print(f"\n{'=' * 60}")
    print(f"TEST: {label}")
    print(f"file_path = \"{file_path}\"")
    print(f"{'=' * 60}")

    directory = os.path.dirname(file_path) or "."
    print(f"\n1. Directory resolved to: \"{directory}\"")

    raw_files = list_local_files(directory)
    print(f"2. Raw list_local_files() output ({len(raw_files)} items):")
    for f in raw_files:
        print(f"     - {f}")

    project_context = get_project_context(file_path)

    print(f"\n3. Final project_context:")
    if project_context is None:
        print(f"     None (correctly fell back)")
    else:
        print(f"     {len(project_context)} sibling files (self excluded):")
        for f in project_context:
            print(f"     - {f}")

    # Verify self-exclusion
    basename = os.path.basename(file_path)
    if project_context and basename in project_context:
        print(f"\n   [FAIL] \"{basename}\" was NOT excluded from sibling list!")
    elif project_context:
        print(f"\n   [PASS] \"{basename}\" correctly excluded from sibling list")

    return project_context


if __name__ == "__main__":
    print("MCP Context-Gathering Test")
    print("(Zero API calls — safe to run freely)\n")

    # --- Test 1: Valid file in the current directory ---
    ctx1 = run_test(
        label="Valid file in current directory",
        file_path="test_sample.py"
    )

    # --- Test 2: Broken/nonexistent directory ---
    ctx2 = run_test(
        label="Nonexistent directory (should fall back to None)",
        file_path="nonexistent_folder/fake_file.py"
    )

    # --- Test 3: File in a real subdirectory ---
    ctx3 = run_test(
        label="File inside ai_agent/ subdirectory",
        file_path="ai_agent/review_service.py"
    )

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Test 1 (valid path):       {'[PASS]' if ctx1 is not None else '[FAIL] expected a list'}")
    print(f"  Test 2 (broken path):      {'[PASS]' if ctx2 is None else '[FAIL] expected None'}")
    print(f"  Test 3 (subdirectory):     {'[PASS]' if ctx3 is not None else '[FAIL] expected a list'}")
    print()

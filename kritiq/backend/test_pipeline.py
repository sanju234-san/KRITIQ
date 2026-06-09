"""
test_pipeline.py — Integration test runner for the full 5-agent LangGraph orchestrator.
Mocks GitHub, Groq, and Playwright dependencies to verify pipeline states and routing.
"""

import os
import sys

# Set up dummy environment variables for settings validation
os.environ["GROQ_API_KEY"] = "mock_groq_key"
os.environ["GITHUB_TOKEN"] = "mock_github_token"
os.environ["GITHUB_WEBHOOK_SECRET"] = "mock_webhook_secret"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DB_NAME"] = "test_db"

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.core.orchestrator import run_pipeline
from app.services.github_service import FileContent
from app.schemas.webhook import WebhookPayload
from app.services.mongo_repository import MongoRepository


# ── Context manager mock for Playwright ──────────────────

class MockPlaywrightContext:
    async def __aenter__(self):
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_browser.new_page.return_value = mock_page
        mock_playwright.chromium.launch.return_value = mock_browser
        return mock_playwright

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# ── Main Test Definition ─────────────────────────────────


async def main():
    print("==========================================")
    print("Testing Full 5-Agent Pipeline Orchestration")
    print("==========================================\n")

    # ── Mock Database Repository ─────────────────────────
    # We will simulate the reports db collection locally in a dictionary
    db_reports = {}

    async def mock_save_report(report):
        doc = report.model_dump(mode="json")
        doc["_id"] = doc.pop("id")
        db_reports[doc["_id"]] = doc
        print(f"   [DB Log] Saved report {doc['_id']} with status '{doc['status']}'")
        return doc["_id"]

    async def mock_get_report(report_id):
        doc = db_reports.get(report_id)
        if not doc:
            return None
        doc_copy = doc.copy()
        doc_copy["id"] = doc_copy.pop("_id")
        from app.schemas.report import ReviewReport
        return ReviewReport.model_validate(doc_copy)

    # ── Mock GitHub Service ──────────────────────────────
    mock_files = [
        FileContent(
            path="main.py",
            content="""# Test Python File
def run():
    print("hello world")
""",
            size=50,
            sha="main_sha_123",
        )
    ]
    mock_fetch = AsyncMock(return_value=mock_files)
    mock_commit = AsyncMock(return_value="commit_sha_xyz987")

    # ── Mock Groq LLM Side Effects ───────────────────────
    # We will run two tests:
    # Test A: Code review returns issues -> auto-fixer runs.
    # Test B: Code review returns NO issues -> auto-fixer is skipped.
    
    test_run_type = "A"  # We toggle this to simulate different code reviews

    # Mock JSON strings
    reviewer_with_issues = """[
        {
            "file_path": "main.py",
            "line_number": 3,
            "severity": "high",
            "category": "bug",
            "description": "Prints a message but has no return value.",
            "suggested_fix": "Add a return statement."
        }
    ]"""
    reviewer_clean = "[]"
    
    # Auto-fixer expects keys: original_code, fixed_code, explanation
    auto_fixer_json = """{
        "original_code": "    print(\\\"hello world\\\")",
        "fixed_code": "    print(\\\"hello world\\\")\\n    return True",
        "explanation": "Added return statement to avoid returning None."
    }"""
    
    uml_mermaid_flow = """
    flowchart TD
        A[main.py] --> B[Run Function]
    """
    
    readme_markdown = """# Codebase Review Summary
- All checks completed successfully.
"""

    async def mock_ainvoke(messages, *args, **kwargs):
        system_prompt = messages[0].content
        if "expert autonomous code reviewer" in system_prompt:
            if test_run_type == "A":
                return MagicMock(content=reviewer_with_issues)
            else:
                return MagicMock(content=reviewer_clean)
        elif "specifically for hardcoded secrets" in system_prompt:
            return MagicMock(content="[]")
        elif "SQL injection (raw queries" in system_prompt:
            return MagicMock(content="[]")
        elif "generate a code fix" in system_prompt:
            return MagicMock(content=auto_fixer_json)
        elif "expert system architect" in system_prompt:
            return MagicMock(content=uml_mermaid_flow)
        elif "expert technical writer" in system_prompt:
            return MagicMock(content=readme_markdown)
        else:
            return MagicMock(content="[]")

    # ── Apply Patches and Execute ────────────────────────
    
    # We patch all external API dependencies
    with patch("app.services.mongo_repository.mongo_repository.save_report", side_effect=mock_save_report), \
         patch("app.services.mongo_repository.mongo_repository.get_report", side_effect=mock_get_report), \
         patch("app.services.github_service.github_service.fetch_files", mock_fetch), \
         patch("app.services.github_service.github_service.commit_file", mock_commit), \
         patch("langchain_groq.ChatGroq.ainvoke", side_effect=mock_ainvoke), \
         patch("playwright.async_api.async_playwright", return_value=MockPlaywrightContext()), \
         patch("app.agents.screenshot_uml.ScreenshotUMLAgent._render_mermaid_api_fallback", return_value="temp/uml/uml.png"):

        # ── TEST RUN A: Issues Found (Fixer executes) ──
        print("--- RUN A: Simulating review WITH issues (expecting auto-fixer execution) ---")
        test_run_type = "A"
        
        payload_a = WebhookPayload(
            repo_url="https://github.com/octocat/test-repo",
            commit_sha="commit_sha_111",
            live_url="https://test-live-app.com",
        )
        
        report_a = await run_pipeline(payload_a)
        
        print("\n   [Results A]")
        print(f"   Status: {report_a.status}")
        print(f"   Flags:  {len(report_a.flags)}")
        print(f"   Fixes:  {len(report_a.fixes)}")
        
        # Verify the fixer executed and saved in the DB
        assert report_a.status == "complete", "Pipeline should finish successfully."
        assert len(report_a.flags) == 1, "Should have 1 flagged issue."
        assert len(report_a.fixes) == 1, "AutoFixer should have committed 1 fix."
        assert report_a.fixes[0].commit_sha == "commit_sha_xyz987", "Fix should have a commit SHA."
        print("\n[OK] Run A completed and verified correctly.")

        # ── TEST RUN B: Clean Codebase (Fixer is skipped) ──
        print("\n--- RUN B: Simulating review WITHOUT issues (expecting auto-fixer skip) ---")
        test_run_type = "B"
        
        payload_b = WebhookPayload(
            repo_url="https://github.com/octocat/clean-repo",
            commit_sha="commit_sha_222",
            live_url="https://clean-live-app.com",
        )
        
        report_b = await run_pipeline(payload_b)
        
        print("\n   [Results B]")
        print(f"   Status: {report_b.status}")
        print(f"   Flags:  {len(report_b.flags)}")
        print(f"   Fixes:  {len(report_b.fixes)}")
        
        # Verify the fixer was skipped and did not run/commit anything
        assert report_b.status == "complete", "Pipeline should finish successfully."
        assert len(report_b.flags) == 0, "Should have 0 flagged issues."
        assert len(report_b.fixes) == 0, "AutoFixer should have been skipped."
        print("\n[OK] Run B completed and verified correctly.")

    print("\n==========================================")
    print("[SUCCESS] ALL PIPELINE INTEGRATION TESTS PASSED!")
    print("==========================================")


if __name__ == "__main__":
    asyncio.run(main())

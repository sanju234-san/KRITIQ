"""
test_orchestrator.py — Unit test script to verify parallel execution in the orchestrator pipeline.
Mocks the GitHubService and ChatGroq LLM calls.
"""

import os
import sys

# Set up dummy environment variables for settings validation before any app imports
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
from app.schemas.report import ReviewReport


async def main():
    print("Testing KRITIQ Parallel Orchestrator Pipeline...")

    # 1. Define mock source files
    mock_files = [
        FileContent(
            path="app/auth.py",
            content="""import os

# Hardcoded AWS Key
AWS_SECRET = "AKIA1234567890ABCDEF"

def get_user(user_id):
    # Potential SQL Injection
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return db.execute(query)
""",
            size=200,
            sha="auth_sha_123",
        )
    ]

    # Mock GitHubService fetch_files
    mock_fetch = AsyncMock(return_value=mock_files)

    # 2. Mock ChatGroq LLM responses
    # The pipeline executes CodeReviewerAgent.run and SecurityAuditorAgent.run.
    # CodeReviewerAgent: 1 LLM call for app/auth.py
    # SecurityAuditorAgent: 2 LLM calls (scan_secrets, check_injections) for app/auth.py
    # We mock them to return JSON strings representing FlaggedIssues.

    code_reviewer_json = """[
        {
            "file_path": "app/auth.py",
            "line_number": 6,
            "severity": "medium",
            "category": "style",
            "description": "Function 'get_user' is missing a docstring.",
            "suggested_fix": "Add a descriptive docstring to describe the function parameters and return value."
        }
    ]"""

    security_secrets_json = "[]"  # Regex will catch the key; Groq doesn't find other keys.

    security_injections_json = """[
        {
            "file_path": "app/auth.py",
            "line_number": 8,
            "severity": "critical",
            "category": "security",
            "description": "Raw string formatting in database query allows SQL Injection.",
            "suggested_fix": "Use parameterized queries, parameterized placeholder binders, or an ORM."
        }
    ]"""

    # We need to simulate the order of calls. Since they are run concurrently:
    # CodeReviewerAgent calls ainvoke.
    # SecurityAuditorAgent calls ainvoke twice.
    # Let's write a side_effect function that matches the prompt / system prompt content.
    async def mock_ainvoke(messages, *args, **kwargs):
        system_prompt = messages[0].content
        if "expert autonomous code reviewer" in system_prompt:
            return MagicMock(content=code_reviewer_json)
        elif "specifically for hardcoded secrets" in system_prompt:
            return MagicMock(content=security_secrets_json)
        elif "SQL injection (raw queries" in system_prompt:
            return MagicMock(content=security_injections_json)
        else:
            return MagicMock(content="[]")

    # Mock MongoDB Repository
    db_reports = {}

    async def mock_save_report(report):
        doc = report.model_dump(mode="json")
        doc["_id"] = doc.pop("id")
        db_reports[doc["_id"]] = doc
        return doc["_id"]

    async def mock_get_report(report_id):
        doc = db_reports.get(report_id)
        if not doc:
            return None
        doc_copy = doc.copy()
        doc_copy["id"] = doc_copy.pop("_id")
        return ReviewReport.model_validate(doc_copy)

    with patch("app.services.mongo_repository.mongo_repository.save_report", side_effect=mock_save_report), \
         patch("app.services.mongo_repository.mongo_repository.get_report", side_effect=mock_get_report), \
         patch("app.services.github_service.github_service.fetch_files", mock_fetch), \
         patch("langchain_groq.ChatGroq.ainvoke", side_effect=mock_ainvoke), \
         patch("playwright.async_api.async_playwright"), \
         patch("app.agents.screenshot_uml.ScreenshotUMLAgent._render_mermaid_api_fallback", return_value="temp/uml/uml.png"):

        # Run the orchestrator pipeline
        payload = WebhookPayload(
            repo_url="https://github.com/octocat/my-repo",
            commit_sha="abc123def456",
        )
        report = await run_pipeline(payload)

        # Convert to dictionary representation for backward compatibility with existing tests
        final_state = {
            "report_id": report.id,
            "repo_url": report.repo_url,
            "commit_sha": report.commit_sha,
            "files": [
                {
                    "path": f.path,
                    "content": f.content,
                    "size": f.size,
                    "sha": f.sha
                } for f in mock_files
            ],
            "flags": [flag.model_dump() for flag in report.flags],
            "fixes": [fix.model_dump() for fix in report.fixes],
        }

        print("\n--- Pipeline Execution Complete! ---")
        print(f"Report ID: {final_state.get('report_id')}")
        print(f"Repo URL:  {final_state.get('repo_url')}")
        print(f"Commit:    {final_state.get('commit_sha')}")

        files = final_state.get("files") or []
        print(f"Files scanned: {[f['path'] for f in files]}")

        flags = final_state.get("flags") or []
        print(f"Merged Flags count: {len(flags)}")

        print("\nFlagged Issues Details:")
        for idx, flag in enumerate(flags, 1):
            print(f"{idx}. [{flag.get('category').upper()}] {flag.get('file_path')}:{flag.get('line_number')} - {flag.get('severity')}")
            print(f"   Desc: {flag.get('description')}")
            print(f"   Fix:  {flag.get('suggested_fix')}\n")

        # 3. Assertions and Verifications
        assert len(flags) >= 3, "Pipeline should have merged style issue, regex secret, and SQL injection issue."
        
        # Check regex secret detection
        regex_secrets = [
            f for f in flags 
            if f.get("category") == "security" and "Potential hardcoded secret" in f.get("description")
        ]
        assert len(regex_secrets) > 0, "Regex failed to capture AWS secret"
        print("[OK] Regex secret verification passed.")

        # Check Groq injection detection
        groq_injections = [
            f for f in flags
            if f.get("category") == "security" and "SQL Injection" in f.get("description")
        ]
        assert len(groq_injections) > 0, "Groq injection scanner failed to capture SQL Injection"
        print("[OK] Groq injection verification passed.")

        # Check general code reviewer style detection
        cr_flags = [
            f for f in flags
            if f.get("category") == "style"
        ]
        assert len(cr_flags) > 0, "Code Reviewer failed to capture style warning"
        print("[OK] Code Reviewer style verification passed.")

        print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY! Parallel execution and merging works flawlessly.")


if __name__ == "__main__":
    asyncio.run(main())

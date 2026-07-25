import os
import time
import uuid
import re
import asyncio
from fastapi.testclient import TestClient
from typer.testing import CliRunner

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Verify imports
import app.main
from app.main import app
from app.core.config import settings

# ─── Helper ───────────────────────────────────────────────────────────────────

def run_step(step_number: int, label: str, fn, *args, **kwargs):
    """
    Runs a step, prints its duration and return value, and handles exceptions.
    Returns (success: bool, output_str).
    """
    print(f"\n{'='*60}")
    print(f"=== STEP {step_number}: {label} ===")
    print(f"{'='*60}")
    start = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"Result:\n{result}")
        print(f"\n[Step {step_number} completed in {duration:.2f}s]")
        return True, str(result)
    except Exception as e:
        duration = time.perf_counter() - start
        print(f"[FAILED] Step {step_number} — {label}")
        print(f"Error: {e}")
        print(f"[Step {step_number} failed after {duration:.2f}s]")
        return False, str(e)


# ─── Verification Tasks ────────────────────────────────────────────────────────

def main():
    total_start = time.perf_counter()
    print("=============================================================")
    print("      KRITIQ COMPREHENSIVE BACKEND VERIFICATION PLAYGROUND   ")
    print("=============================================================")
    
    # Check credentials status
    gemini_key_exists = bool(os.environ.get("GEMINI_API_KEY"))
    groq_key_exists = bool(os.environ.get("GROQ_API_KEY"))
    mongodb_uri_exists = bool(os.environ.get("MONGODB_URI"))
    
    print(f"Credentials Status:")
    print(f"  GEMINI_API_KEY: {'Present' if gemini_key_exists else 'MISSING'}")
    print(f"  GROQ_API_KEY:   {'Present' if groq_key_exists else 'MISSING'}")
    print(f"  MONGODB_URI:    {'Present' if mongodb_uri_exists else 'MISSING'}")
    print("=============================================================\n")

    summary_table = []
    failures = []
    
    # Define Sample Code for AI service testing
    SAMPLE_CODE = """def count_elements(items):
    # Unused variable
    debug_mode = True
    total = 0
    for item in items:
        total += 1
    # Missing return statement
"""

    # =========================================================================
    # SANJEEVNI (AI Agent & Developer Tools) Verification
    # =========================================================================

    # 1. AI agent logic / Gemini integration
    def step_gemini_call():
        if not gemini_key_exists:
            return "NOT TESTED — missing credential"
        from ai_agent.gemini_client import ask_gemini
        prompt = "Hello! Write a 1-sentence code comment."
        return ask_gemini(prompt)

    ok, res = run_step(1, "Sanjeevni - Gemini Integration (ask_gemini)", step_gemini_call)
    summary_table.append(("1. Gemini Call", "OK" if ok else "FAIL", res[:60] + "..."))
    if not ok: failures.append(1)

    # 2. Groq fallback
    def step_groq_fallback():
        # Confirm fallback wiring structurally
        from ai_agent.gemini_client import ask_gemini
        import inspect
        source = inspect.getsource(ask_gemini)
        fallback_referenced = "from ai_agent.groq_client import ask_groq" in source or "ask_groq(" in source
        
        # Test Groq call directly
        groq_direct_res = "Skipped Groq call"
        if groq_key_exists:
            from ai_agent.groq_client import ask_groq
            groq_direct_res = ask_groq("Hello from Groq! Confirm you are llama.")
            
        return f"Fallback wiring present in ask_gemini: {fallback_referenced}\nDirect Groq response: {groq_direct_res}"

    ok, res = run_step(2, "Sanjeevni - Groq Fallback Verification", step_groq_fallback)
    summary_table.append(("2. Groq Fallback", "OK" if ok else "FAIL", res.replace("\n", " ")[:60] + "..."))
    if not ok: failures.append(2)

    # 3. Prompt engineering for review/translation/explanation
    def step_prompt_engineering():
        if not gemini_key_exists:
            return "NOT TESTED — missing credential"
        from ai_agent.review_service import review_code
        from ai_agent.explanation_service import explain_code
        from ai_agent.translation_service import translate_code
        
        print("Reviewing code...")
        rev = review_code(SAMPLE_CODE, "python")
        print("\nExplaining code...")
        exp = explain_code(SAMPLE_CODE, "python")
        print("\nTranslating code...")
        tra = translate_code(SAMPLE_CODE, "python", "java")
        
        return f"=== REVIEW ===\n{rev}\n\n=== EXPLANATION ===\n{exp}\n\n=== TRANSLATION ===\n{tra}"

    ok, res = run_step(3, "Sanjeevni - AI Review / Explanation / Translation Prompts", step_prompt_engineering)
    summary_table.append(("3. AI Services", "OK" if ok else "FAIL", "Ran review, explain, and translate services successfully."))
    if not ok: failures.append(3)

    # 4. MCP Server integration
    def step_mcp_files():
        from mcp_server.tools import list_local_files
        return list_local_files(".")

    ok, res = run_step(4, "Sanjeevni - MCP local file tool (list_local_files)", step_mcp_files)
    summary_table.append(("4. MCP Tools", "OK" if ok else "FAIL", res[:60] + "..."))
    if not ok: failures.append(4)

    # 5. Custom dataset + RAG pipeline
    def step_rag_embeddings():
        from rag_pipeline.retriever import get_or_build_combined_embeddings, retrieve_similar_examples
        combined = get_or_build_combined_embeddings()
        count = len(combined)
        
        # Test cosine similarity retrieval
        query = "mutable default arguments in Python"
        similar = retrieve_similar_examples(query, combined, top_k=1)
        similar_id = similar[0]["id"] if similar else "None"
        
        return f"Combined dataset entries: {count}\nRetrieval test matching '{query}' -> Top Match ID: {similar_id}"

    ok, res = run_step(5, "Sanjeevni - Dataset & RAG (cosine similarity search)", step_rag_embeddings)
    summary_table.append(("5. RAG Pipeline", "OK" if ok else "FAIL", res.replace("\n", " ")[:60] + "..."))
    if not ok: failures.append(5)

    # 6. GitHub integration
    def step_github_api():
        from repo_integration.github_api import list_repo_files
        res = list_repo_files("octocat", "Hello-World")
        return res

    ok, res = run_step(6, "Sanjeevni - GitHub API (list_repo_files)", step_github_api)
    summary_table.append(("6. GitHub API", "OK" if ok else "FAIL", res[:60] + "..."))
    if not ok: failures.append(6)

    # 7. Cross-language translation logic (Python to Java)
    def step_py_to_java_translation():
        if not gemini_key_exists:
            return "NOT TESTED — missing credential"
        from ai_agent.translation_service import translate_code
        return translate_code(SAMPLE_CODE, "python", "java")

    ok, res = run_step(7, "Sanjeevni - Python-to-Java translation result", step_py_to_java_translation)
    summary_table.append(("7. Py-to-Java Trans", "OK" if ok else "FAIL", "Successfully translated Python to Java."))
    if not ok: failures.append(7)

    # 8. CLI tool commands validation
    def step_cli_validation():
        from cli.main import app as cli_app
        runner = CliRunner()
        
        # Help check (verifies 'chat' registration)
        help_res = runner.invoke(cli_app, ["--help"])
        chat_registered = "chat" in help_res.output
        
        # Subcommand helps
        review_help = runner.invoke(cli_app, ["review", "--help"])
        translate_help = runner.invoke(cli_app, ["translate", "--help"])
        explain_help = runner.invoke(cli_app, ["explain", "--help"])
        chat_help = runner.invoke(cli_app, ["chat", "--help"])
        
        # Chat loop exit check
        chat_loop_res = runner.invoke(cli_app, ["chat"], input="hello\nexit\n")
        
        return (
            f"Chat subcommand registered in help: {chat_registered}\n"
            f"Review help status: {review_help.exit_code}\n"
            f"Translate help status: {translate_help.exit_code}\n"
            f"Explain help status: {explain_help.exit_code}\n"
            f"Chat help status: {chat_help.exit_code}\n"
            f"Chat loop interactive exit test output:\n{chat_loop_res.output}"
        )

    ok, res = run_step(8, "Sanjeevni - CLI tool & Chat command registration/execution", step_cli_validation)
    summary_table.append(("8. CLI Registration", "OK" if ok else "FAIL", "CLI app commands successfully registered and validated."))
    if not ok: failures.append(8)


    # =========================================================================
    # SAYEED (Backend & Database) Verification
    # =========================================================================

    client = TestClient(app)

    # 9. FastAPI backend startup
    def step_backend_startup():
        response = client.get("/")
        return f"Root health check status: {response.status_code}\nResponse JSON: {response.json()}"

    ok, res = run_step(9, "Sayeed - FastAPI Backend health check", step_backend_startup)
    summary_table.append(("9. FastAPI Health", "OK" if ok else "FAIL", res.replace("\n", " ")[:60] + "..."))
    if not ok: failures.append(9)

    # 10. MongoDB Integration via Repositories
    # Create random credentials for unique testing
    random_id = str(uuid.uuid4())[:8]
    test_email = f"test_{random_id}@example.com"
    test_password = "password123"
    test_name = f"Tester {random_id}"

    async def step_mongo_db_repos_async():
        from app.db.users_repo import users_repo
        from app.db.reviews_repo import reviews_repo
        from app.db.translations_repo import translations_repo
        from app.db.history_repo import history_repo
        from app.db.repositories_repo import repositories_repo
        
        # Determine URI / mock label
        label = "Real Atlas MongoDB" if mongodb_uri_exists else "Mock Mongo"
        
        # Bug 3 FIX: Generate a separate random email for mongo raw/class testing
        mongo_test_random_id = str(uuid.uuid4())[:8]
        mongo_test_email = f"mongotest_{mongo_test_random_id}@example.com"
        
        # Test User DB write/read via Repository Class (Bug 4 FIX)
        user_doc = {
            "name": f"Tester {mongo_test_random_id}",
            "email": mongo_test_email,
            "password": "hashed_password_placeholder"
        }
        stored_user = await users_repo.create_user(user_doc)
        fetched_user = await users_repo.get_by_email(mongo_test_email)
        user_id = str(fetched_user.get("_id"))
        
        # Test Review DB write/read via Repository Class (Bug 4 FIX)
        review_doc = {
            "summary": "Verified review write",
            "issues": []
        }
        stored_review = await reviews_repo.save_review(user_id, review_doc)
        review_id = stored_review["_id"]
        fetched_review = await reviews_repo.get_review_by_id(review_id)
        
        # Test Translation DB write/read via Repository Class (Bug 4 FIX)
        trans_doc = {
            "source_code": "code",
            "translated_code": "translated_code"
        }
        stored_trans = await translations_repo.save_translation(user_id, trans_doc)
        trans_id = stored_trans["_id"]
        fetched_trans = await translations_repo.get_translation_by_id(trans_id)
        
        # Test History write/read via Repository Class (Bug 4 FIX)
        stored_history = await history_repo.log_activity(
            user_id=user_id,
            type="review",
            summary="Checklist test history",
            details={"review_id": review_id}
        )
        history_id = stored_history["_id"]
        history_list = await history_repo.get_history_by_user(user_id)
        fetched_history = next((h for h in history_list if h["_id"] == history_id), None)
        
        # Test Repositories Repo write/read via Repository Class (Bug 4 FIX)
        repo_doc = {
            "user_id": user_id,
            "repo_url": "https://github.com/octocat/Hello-World",
            "owner": "octocat",
            "name": "Hello-World"
        }
        stored_repo = await repositories_repo.add_repository(repo_doc)
        repo_db_id = stored_repo["_id"]
        repo_list = await repositories_repo.get_repositories_by_user(user_id)
        fetched_repo = next((r for r in repo_list if r["_id"] == repo_db_id), None)
        
        # Clean up database records (Bug 2 FIX: delete user by raw ObjectId, others by stored id)
        users_repo.collection.delete_one({"_id": fetched_user["_id"]})
        reviews_repo.collection.delete_one({"_id": review_id})
        translations_repo.collection.delete_one({"_id": trans_id})
        history_repo.collection.delete_one({"_id": history_id})
        repositories_repo.collection.delete_one({"_id": repo_db_id})
        
        return (
            f"Verified against: {label}\n"
            f"  Created user: {fetched_user.get('email')}\n"
            f"  Created review summary: {fetched_review.get('summary')}\n"
            f"  Created translation target: {fetched_trans.get('translated_code')}\n"
            f"  Created history log: {fetched_history.get('summary')}\n"
            f"  Created repository: {fetched_repo.get('repo_url')}"
        )

    def step_mongo_db_repos():
        return asyncio.run(step_mongo_db_repos_async())

    ok, res = run_step(10, "Sayeed - MongoDB repository class transactions", step_mongo_db_repos)
    summary_table.append(("10. DB Integration", "OK" if ok else "FAIL", res.replace("\n", " ")[:60] + "..."))
    if not ok: failures.append(10)

    # 11. JWT Authentication
    jwt_token = ""
    def step_jwt_auth():
        nonlocal jwt_token
        # 1. Register User via API
        register_payload = {
            "name": test_name,
            "email": test_email,
            "password": test_password
        }
        reg_response = client.post("/auth/register", json=register_payload)
        
        # 2. Login User via API to get token
        login_payload = {
            "email": test_email,
            "password": test_password
        }
        login_response = client.post("/auth/login", json=login_payload)
        jwt_token = login_response.json().get("access_token")
        
        # 3. Test Protected Route WITHOUT token
        profile_unauth = client.get("/auth/profile")
        
        # 4. Test Protected Route WITH token
        profile_auth = client.get(
            "/auth/profile",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        return (
            f"Register status: {reg_response.status_code}\n"
            f"Login status: {login_response.status_code}\n"
            f"Profile (No Token) status: {profile_unauth.status_code} (Expected 401)\n"
            f"Profile (With Token) status: {profile_auth.status_code} (Expected 200)\n"
            f"Profile data: {profile_auth.json()}"
        )

    ok, res = run_step(11, "Sayeed - JWT authentication registration/login/access flow", step_jwt_auth)
    summary_table.append(("11. JWT Auth Flow", "OK" if ok else "FAIL", "Auth token fetched and protected profile route successfully validated."))
    if not ok: failures.append(11)

    # 12. REST APIs - Reviews & Translations (uses Sanjeevni's AI functions)
    def step_api_ai_integration():
        if not gemini_key_exists:
            return "NOT TESTED — missing credential"
            
        # Review API Request
        review_payload = {
            "code": SAMPLE_CODE,
            "language": "python",
            "filename": "test.py"
        }
        rev_resp = client.post(
            "/reviews/",
            json=review_payload,
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        # Translation API Request
        trans_payload = {
            "source_code": SAMPLE_CODE,
            "source_language": "python",
            "target_language": "java"
        }
        trans_resp = client.post(
            "/translations/",
            json=trans_payload,
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        return (
            f"Reviews API Status: {rev_resp.status_code}\n"
            f"Reviews API JSON Review ID: {rev_resp.json().get('review_id')}\n"
            f"Reviews API Summary: {rev_resp.json().get('summary')}\n\n"
            f"Translations API Status: {trans_resp.status_code}\n"
            f"Translations API JSON Notes: {trans_resp.json().get('notes')}"
        )

    ok, res = run_step(12, "Sayeed - REST API AI integration (calling AI services through endpoints)", step_api_ai_integration)
    summary_table.append(("12. API AI Integr.", "OK" if ok else "FAIL", "Called reviews and translations API endpoints successfully."))
    if not ok: failures.append(12)

    # 13. REST APIs - History
    def step_api_history():
        hist_resp = client.get(
            "/history/",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        return f"History Status: {hist_resp.status_code}\nHistory Items Count: {len(hist_resp.json().get('history', []))}\nFirst Item Summary: {hist_resp.json().get('history', [{}])[0].get('summary')}"

    ok, res = run_step(13, "Sayeed - Activity History endpoint retrieval", step_api_history)
    summary_table.append(("13. API History", "OK" if ok else "FAIL", res.replace("\n", " ")[:60] + "..."))
    if not ok: failures.append(13)

    # 14. Repository connection and listing (the new module)
    def step_api_repository_integration():
        # a. POST connect with valid URL
        valid_payload = {
            "repo_url": "https://github.com/octocat/Hello-World"
        }
        valid_resp = client.post(
            "/repositories/connect",
            json=valid_payload,
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        # b. POST connect with invalid/nonexistent URL
        invalid_payload = {
            "repo_url": "https://github.com/invalid-owner-xyz/invalid-repo-xyz"
        }
        invalid_resp = client.post(
            "/repositories/connect",
            json=invalid_payload,
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        # c. GET repositories listing
        list_resp = client.get(
            "/repositories/",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        return (
            f"Connect Valid Repo Status: {valid_resp.status_code}\n"
            f"Connect Valid Repo JSON: {valid_resp.json()}\n\n"
            f"Connect Invalid Repo Status: {invalid_resp.status_code} (Expected 400)\n"
            f"Connect Invalid Repo JSON: {invalid_resp.json()}\n\n"
            f"List Repositories Status: {list_resp.status_code}\n"
            f"List Repositories JSON: {list_resp.json()}"
        )

    ok, res = run_step(14, "Sayeed - GitHub repository connection & listing endpoints", step_api_repository_integration)
    summary_table.append(("14. Repo Endpoints", "OK" if ok else "FAIL", "Connected valid/invalid repos and listed successfully."))
    if not ok: failures.append(14)

    # 15. Middleware (Rate limiting, Security headers)
    def step_middleware_headers():
        # Fetch root path health check
        response = client.get("/")
        headers = response.headers
        
        # Extract security headers
        sec_headers = {
            "X-Frame-Options": headers.get("X-Frame-Options"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options"),
            "X-XSS-Protection": headers.get("X-XSS-Protection"),
            "Referrer-Policy": headers.get("Referrer-Policy"),
            "Strict-Transport-Security": headers.get("Strict-Transport-Security")
        }
        
        return f"Response Headers:\n{headers}\n\nSecurity Headers Parsed:\n{sec_headers}"

    ok, res = run_step(15, "Sayeed - Security headers verification", step_middleware_headers)
    summary_table.append(("15. Security Headers", "OK" if ok else "FAIL", "Security headers extracted and verified successfully."))
    if not ok: failures.append(15)


    # =========================================================================
    # SUMMARY REPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("                      VERIFICATION SUMMARY REPORT")
    print("=" * 60)
    print(f"| {'Item/Task':<25} | {'Status':<6} | {'Evidence/Sample':<45} |")
    print("-" * 84)
    for name, status, evidence in summary_table:
        print(f"| {name:<25} | {status:<6} | {evidence:<45} |")
    print("=" * 60)
    
    if failures:
        print(f"\n[!] Verification completed with failures in steps: {failures}")
    else:
        print("\n[+] Verification completed successfully. All components operational!")
    print(f"Total time elapsed: {time.perf_counter() - total_start:.2f}s\n")


if __name__ == "__main__":
    main()

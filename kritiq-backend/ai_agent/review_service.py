import os
from ai_agent.prompts.review_prompt import build_review_prompt
from ai_agent.gemini_client import ask_gemini


def review_code(code: str, language: str = "python", file_path: str = None, repo_owner: str = None, repo_name: str = None) -> str:
    """
    Builds a review prompt and calls Gemini to review the provided code.
    If RAG datasets are available, retrieves similar examples from ALL
    dataset files combined and includes them in the prompt as reference material.

    Project context (MCP sibling-file) retrieval fires in two scenarios:
      1. `file_path` provided (CLI path) — scans the local directory for siblings.
      2. `repo_owner` + `repo_name` + `file_path` provided (web path from connected
         GitHub repo) — uses MCP's list_github_repo_files tool to list siblings at
         the same directory depth inside the repository.

    Falls back gracefully to a plain prompt if either enrichment step fails.
    When no repo context is available at all (raw paste / upload with no repo),
    MCP sibling retrieval is correctly skipped (no repo to retrieve siblings from).
    RAG best-practice examples are still included regardless, if available.
    """
    retrieved_examples = None
    project_context = None

    # --- MCP Context: gather sibling files ---
    if file_path and repo_owner and repo_name:
        # Web path: connected GitHub repo — list siblings at the same folder path
        try:
            from mcp_server.tools import list_github_repo_files

            directory = os.path.dirname(file_path) or ""
            sibling_entries = list_github_repo_files(repo_owner, repo_name, directory)

            if sibling_entries and not any(f.startswith("Error:") for f in sibling_entries):
                basename = os.path.basename(file_path)
                # Entries at a GitHub path include both files and directories; we only
                # want sibling files (or any names) for context; filter out the file
                # being reviewed itself.
                project_context = [f for f in sibling_entries if f != basename]
                if project_context:
                    print(f"[MCP GITHUB] Found {len(project_context)} sibling files for project context in {repo_owner}/{repo_name}/{directory}.")
                else:
                    project_context = None
        except Exception as e:
            print(f"[MCP GITHUB WARNING] Could not gather GitHub project context — skipping. Reason: {e}")
            project_context = None

    elif file_path:
        # CLI path: local filesystem — list siblings in the same directory
        try:
            from mcp_server.tools import list_local_files

            directory = os.path.dirname(file_path) or "."
            sibling_files = list_local_files(directory)

            # Filter out error strings returned by list_local_files on failure
            if sibling_files and not any(f.startswith("Error:") for f in sibling_files):
                # Exclude the file itself from the sibling list
                basename = os.path.basename(file_path)
                project_context = [f for f in sibling_files if f != basename]
                if project_context:
                    print(f"[MCP LOCAL] Found {len(project_context)} sibling files for project context.")
                else:
                    project_context = None
        except Exception as e:
            print(f"[MCP LOCAL WARNING] Could not gather project context — skipping. Reason: {e}")
            project_context = None
    else:
        # No repo context available (raw paste / upload without repo association)
        # MCP sibling retrieval correctly skipped — nothing to retrieve siblings from.
        print("[MCP] No file_path + repo context provided — skipping MCP sibling-file retrieval (RAG examples still active).")

    # --- RAG Retrieval: find similar dataset examples ---
    try:
        from rag_pipeline.retriever import get_or_build_combined_embeddings, retrieve_similar_examples

        dataset_with_embeddings = get_or_build_combined_embeddings()
        retrieved_examples = retrieve_similar_examples(code, dataset_with_embeddings, top_k=2)
        print(f"[RAG] Retrieved {len(retrieved_examples)} reference examples for review prompt.")
    except Exception as e:
        print(f"[RAG WARNING] Could not retrieve examples — falling back to plain prompt. Reason: {e}")
        retrieved_examples = None

    prompt = build_review_prompt(code, language, retrieved_examples=retrieved_examples, project_context=project_context)

    # Trace / debug log so verification scripts can confirm MCP context actually
    # landed in the prompt sent to Gemini.
    if project_context:
        print(f"[PROMPT TRACE] Project context section INCLUDED in Gemini prompt with {len(project_context)} sibling files: {project_context}")
    else:
        print("[PROMPT TRACE] No project context section in Gemini prompt.")

    return ask_gemini(prompt)

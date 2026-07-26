import os
from ai_agent.prompts.explanation_prompt import build_explanation_prompt
from ai_agent.gemini_client import ask_gemini


def explain_code(code: str, language: str = "python", file_path: str = None, repo_owner: str = None, repo_name: str = None) -> str:
    """
    Calls build_explanation_prompt, passes the result to ask_gemini,
    and returns the raw text response.
    Enriches with RAG examples and project context from siblings if possible.

    MCP sibling-file context fires if:
      1. `file_path` + `repo_owner` + `repo_name` are set (web path, GitHub repo)
         — uses list_github_repo_files to find siblings at the same directory level.
      2. Only `file_path` is set (CLI path, local filesystem).
    Otherwise (no file context), MCP retrieval is gracefully skipped (no repo
    available to pull siblings from). RAG examples still run regardless.
    """
    retrieved_examples = None
    project_context = None

    # --- MCP Context: gather sibling files ---
    if file_path and repo_owner and repo_name:
        try:
            from mcp_server.tools import list_github_repo_files

            directory = os.path.dirname(file_path) or ""
            sibling_entries = list_github_repo_files(repo_owner, repo_name, directory)

            if sibling_entries and not any(f.startswith("Error:") for f in sibling_entries):
                basename = os.path.basename(file_path)
                project_context = [f for f in sibling_entries if f != basename]
                if project_context:
                    print(f"[MCP GITHUB EXPLAIN] Found {len(project_context)} siblings for context in {repo_owner}/{repo_name}/{directory}.")
                else:
                    project_context = None
        except Exception as e:
            print(f"[MCP GITHUB EXPLAIN WARNING] Could not gather GitHub project context — skipping. Reason: {e}")
            project_context = None

    elif file_path:
        # CLI path: local filesystem — list siblings in the same directory
        try:
            from mcp_server.tools import list_local_files

            directory = os.path.dirname(file_path) or "."
            sibling_files = list_local_files(directory)

            if sibling_files and not any(f.startswith("Error:") for f in sibling_files):
                basename = os.path.basename(file_path)
                project_context = [f for f in sibling_files if f != basename]
                if project_context:
                    print(f"[MCP LOCAL EXPLAIN] Found {len(project_context)} sibling files for project context.")
                else:
                    project_context = None
        except Exception as e:
            print(f"[MCP LOCAL EXPLAIN WARNING] Could not gather project context — skipping. Reason: {e}")
            project_context = None

    # --- RAG Retrieval: find similar dataset examples ---
    try:
        from rag_pipeline.retriever import get_or_build_combined_embeddings, retrieve_similar_examples

        dataset_with_embeddings = get_or_build_combined_embeddings()
        retrieved_examples = retrieve_similar_examples(code, dataset_with_embeddings, top_k=2)
        print(f"[RAG] Retrieved {len(retrieved_examples)} reference examples for explanation prompt.")
    except Exception as e:
        print(f"[RAG WARNING] Could not retrieve examples — falling back to plain prompt. Reason: {e}")
        retrieved_examples = None

    prompt = build_explanation_prompt(
        code, language,
        retrieved_examples=retrieved_examples,
        project_context=project_context
    )

    if project_context:
        print(f"[EXPLAIN PROMPT TRACE] Project context section INCLUDED with {len(project_context)} sibling files: {project_context}")
    else:
        print("[EXPLAIN PROMPT TRACE] No project context section in the explanation prompt.")

    return ask_gemini(prompt)


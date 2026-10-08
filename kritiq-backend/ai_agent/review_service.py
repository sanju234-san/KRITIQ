import os
from ai_agent.prompts.review_prompt import build_review_prompt
from ai_agent.gemini_client import ask_gemini


def review_code(
    code: str,
    language: str = "python",
    file_path: str = None,
    repo_owner: str = None,
    repo_name: str = None
) -> str:
    """
    Builds a review prompt and calls Gemini to review the provided code.

    If RAG datasets are available, retrieves similar examples from ALL
    dataset files combined and includes them in the prompt as reference material.

    Project context retrieval works in two scenarios:
      1. file_path provided (CLI path)
      2. repo_owner + repo_name + file_path provided (GitHub repo path)

    Falls back gracefully if enrichment fails.

    The review response is explicitly requested as JSON so that the
    review parser receives the expected structured output.
    """

    retrieved_examples = None
    project_context = None

    # ---------------------------------------------------------
    # MCP Context: gather sibling files
    # ---------------------------------------------------------
    if file_path and repo_owner and repo_name:
        try:
            from mcp_server.tools import list_github_repo_files

            directory = os.path.dirname(file_path) or ""

            sibling_entries = list_github_repo_files(
                repo_owner,
                repo_name,
                directory
            )

            if sibling_entries and not any(
                f.startswith("Error:") for f in sibling_entries
            ):
                basename = os.path.basename(file_path)

                project_context = [
                    f for f in sibling_entries
                    if f != basename
                ]

                if project_context:
                    print(
                        f"[MCP GITHUB] Found {len(project_context)} "
                        f"sibling files for project context in "
                        f"{repo_owner}/{repo_name}/{directory}."
                    )
                else:
                    project_context = None

        except Exception as e:
            print(
                f"[MCP GITHUB WARNING] Could not gather GitHub "
                f"project context — skipping. Reason: {e}"
            )
            project_context = None

    elif file_path:
        try:
            from mcp_server.tools import list_local_files

            directory = os.path.dirname(file_path) or "."

            sibling_files = list_local_files(directory)

            if sibling_files and not any(
                f.startswith("Error:") for f in sibling_files
            ):
                basename = os.path.basename(file_path)

                project_context = [
                    f for f in sibling_files
                    if f != basename
                ]

                if project_context:
                    print(
                        f"[MCP LOCAL] Found {len(project_context)} "
                        f"sibling files for project context."
                    )
                else:
                    project_context = None

        except Exception as e:
            print(
                f"[MCP LOCAL WARNING] Could not gather project "
                f"context — skipping. Reason: {e}"
            )
            project_context = None

    else:
        print(
            "[MCP] No file_path + repo context provided — "
            "skipping MCP sibling-file retrieval "
            "(RAG examples still active)."
        )

    # ---------------------------------------------------------
    # RAG Retrieval
    # ---------------------------------------------------------
    try:
        from rag_pipeline.retriever import (
            get_or_build_combined_embeddings,
            retrieve_similar_examples
        )

        dataset_with_embeddings = get_or_build_combined_embeddings()

        retrieved_examples = retrieve_similar_examples(
            code,
            dataset_with_embeddings,
            top_k=2
        )

        print(
            f"[RAG] Retrieved {len(retrieved_examples)} "
            f"reference examples for review prompt."
        )

    except Exception as e:
        print(
            f"[RAG WARNING] Could not retrieve examples — "
            f"falling back to plain prompt. Reason: {e}"
        )
        retrieved_examples = None

    # ---------------------------------------------------------
    # Build review prompt
    # ---------------------------------------------------------
    prompt = build_review_prompt(
        code,
        language,
        retrieved_examples=retrieved_examples,
        project_context=project_context
    )

    # ---------------------------------------------------------
    # Prompt trace
    # ---------------------------------------------------------
    if project_context:
        print(
            f"[PROMPT TRACE] Project context section INCLUDED "
            f"in Gemini prompt with {len(project_context)} "
            f"sibling files: {project_context}"
        )
    else:
        print(
            "[PROMPT TRACE] No project context section "
            "in Gemini prompt."
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Code Review requires structured JSON output.
    # ---------------------------------------------------------
    return ask_gemini(prompt, "json")
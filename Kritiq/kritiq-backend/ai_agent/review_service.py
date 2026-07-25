import os
from ai_agent.prompts.review_prompt import build_review_prompt
from ai_agent.gemini_client import ask_gemini


def review_code(code: str, language: str = "python", file_path: str = None) -> str:
    """
    Builds a review prompt and calls Gemini to review the provided code.
    If RAG datasets are available, retrieves similar examples from ALL
    dataset files combined and includes them in the prompt as reference material.
    If file_path is provided, gathers sibling filenames from the same directory
    via MCP tools and includes them as project context in the prompt.
    Falls back gracefully to a plain prompt if either enrichment step fails.
    """
    retrieved_examples = None
    project_context = None

    # --- MCP Context: gather sibling files (local filesystem, zero API cost) ---
    if file_path:
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
                    print(f"[MCP] Found {len(project_context)} sibling files for project context.")
                else:
                    project_context = None
        except Exception as e:
            print(f"[MCP WARNING] Could not gather project context — skipping. Reason: {e}")
            project_context = None

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
    return ask_gemini(prompt)

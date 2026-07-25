import os
from ai_agent.prompts.translation_prompt import build_translation_prompt
from ai_agent.gemini_client import ask_gemini


def translate_code(code: str, source_language: str, target_language: str, file_path: str = None) -> str:
    """
    Calls build_translation_prompt, passes the result to ask_gemini,
    and returns the raw text response.
    Enriches with RAG examples and project context from siblings if possible.
    """
    retrieved_examples = None
    project_context = None

    # --- MCP Context: gather sibling files (local filesystem, zero API cost) ---
    if file_path:
        try:
            from mcp_server.tools import list_local_files

            directory = os.path.dirname(file_path) or "."
            sibling_files = list_local_files(directory)

            if sibling_files and not any(f.startswith("Error:") for f in sibling_files):
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
        print(f"[RAG] Retrieved {len(retrieved_examples)} reference examples for translation prompt.")
    except Exception as e:
        print(f"[RAG WARNING] Could not retrieve examples — falling back to plain prompt. Reason: {e}")
        retrieved_examples = None

    prompt = build_translation_prompt(
        code, source_language, target_language,
        retrieved_examples=retrieved_examples,
        project_context=project_context
    )
    return ask_gemini(prompt)


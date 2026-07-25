import json
import math
import os
from rag_pipeline.embeddings import get_embedding


def load_dataset_with_embeddings(filepath: str) -> list[dict]:
    """
    Loads the JSON dataset file, generates embeddings for each entry by combining
    code_snippet + explanation, and returns the dataset entries updated with an
    'embedding' field.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    if not isinstance(dataset, list):
        raise ValueError("Dataset root must be a JSON array (list).")

    print(f"Loaded {len(dataset)} entries from {filepath}. Generating embeddings...")

    for index, entry in enumerate(dataset):
        entry_id = entry.get("id", f"index_{index}")
        print(f"Generating embedding for {entry_id}...")

        # Combine code_snippet and explanation for a holistic semantic representation
        combined_text = f"code_snippet: {entry.get('code_snippet', '')}\nexplanation: {entry.get('explanation', '')}"
        
        # Get embedding vector
        entry["embedding"] = get_embedding(combined_text)

    print("All dataset embeddings generated successfully.")
    return dataset


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculates the cosine similarity between two numeric vectors using Python's math module.
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be of equal length.")

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def retrieve_similar_examples(query_text: str, dataset_with_embeddings: list[dict], top_k: int = 3) -> list[dict]:
    """
    Generates an embedding for query_text and compares it against all dataset entries.
    Returns the top_k most similar entries sorted by similarity score (highest first).
    """
    print(f"Generating embedding for query text...")
    query_embedding = get_embedding(query_text)

    scored_entries = []
    for entry in dataset_with_embeddings:
        if "embedding" not in entry:
            continue
        
        similarity = cosine_similarity(query_embedding, entry["embedding"])
        
        # Create a copy of the entry to avoid side effects, and store similarity
        entry_copy = entry.copy()
        # Remove the large embedding vector from the output to keep it clean and readable
        if "embedding" in entry_copy:
            del entry_copy["embedding"]
            
        entry_copy["similarity_score"] = similarity
        scored_entries.append(entry_copy)

    # Sort by similarity score descending
    scored_entries.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_entries[:top_k]


def get_or_build_cached_embeddings(filepath: str, cache_path: str = None) -> list[dict]:
    """
    Loads embeddings from a cache file if it exists.
    If not, builds fresh embeddings, saves them to the cache file, and returns them.
    """
    if cache_path is None:
        base, ext = os.path.splitext(filepath)
        cache_path = f"{base}.embeddings.json"

    if os.path.exists(cache_path):
        print(f"Loading dataset embeddings from cache file: {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load embeddings cache from {cache_path}: {e}. Re-building...")

    # Generate fresh embeddings
    print(f"No valid cache found at {cache_path}. Building fresh embeddings...")
    dataset_with_embeddings = load_dataset_with_embeddings(filepath)

    # Save to cache file
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(dataset_with_embeddings, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved embeddings to cache file: {cache_path}")
    except Exception as e:
        print(f"Warning: Failed to write embeddings cache to {cache_path}: {e}")

    return dataset_with_embeddings


def load_all_dataset_files(directory: str = "dataset/processed") -> list[str]:
    """
    Scans the given directory for all .json files, excluding any file
    ending in '.embeddings.json' (those are cache files, not source datasets).
    Returns a list of full file paths found.
    """
    if not os.path.isdir(directory):
        print(f"Warning: Directory {directory} does not exist.")
        return []

    dataset_files = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json") and not filename.endswith(".embeddings.json"):
            dataset_files.append(os.path.join(directory, filename))

    return dataset_files


def get_or_build_combined_embeddings(
    directory: str = "dataset/processed",
    cache_path: str = "dataset/processed/_combined.embeddings.json"
) -> list[dict]:
    """
    Discovers all source dataset JSON files in the directory, builds or loads
    cached embeddings for each one individually (reusing per-file caches),
    combines them into a single list, and caches the combined result.

    If the combined cache already exists, loads and returns it directly.
    """
    # Check for existing combined cache first
    if os.path.exists(cache_path):
        print(f"Loading combined dataset embeddings from cache: {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                combined = json.load(f)
            print(f"Loaded {len(combined)} total entries from combined cache.")
            return combined
        except Exception as e:
            print(f"Warning: Failed to load combined cache from {cache_path}: {e}. Rebuilding...")

    # Discover all source dataset files
    source_files = load_all_dataset_files(directory)
    if not source_files:
        print(f"No dataset files found in {directory}.")
        return []

    print(f"Found {len(source_files)} dataset file(s) to combine:")
    for f in source_files:
        print(f"  - {f}")

    # Load/build per-file embeddings (reuses individual caches)
    combined = []
    for filepath in source_files:
        print(f"\nProcessing: {filepath}")
        file_entries = get_or_build_cached_embeddings(filepath)
        combined.extend(file_entries)

    print(f"\nCombined {len(combined)} total entries from {len(source_files)} file(s).")

    # Save combined cache
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        print(f"Saved combined embeddings cache to: {cache_path}")
    except Exception as e:
        print(f"Warning: Failed to write combined cache to {cache_path}: {e}")

    return combined


if __name__ == "__main__":
    # Test Query: A function that uses a bare except clause
    QUERY_SNIPPET = """
def load_data(file_path):
    try:
        with open(file_path) as f:
            return f.read()
    except:
        return ""
"""
    DATASET_PATH = "dataset/processed/bad_practice.json"

    print("=== STARTING RETRIEVER TEST ===")
    try:
        # 1. Load dataset and generate embeddings
        dataset_with_emb = load_dataset_with_embeddings(DATASET_PATH)

        # 2. Search for similar entries
        print(f"\nSearching for examples similar to query snippet:\n{QUERY_SNIPPET}")
        results = retrieve_similar_examples(QUERY_SNIPPET, dataset_with_emb, top_k=3)

        # 3. Print results
        print("\n" + "=" * 60)
        print("TOP 3 MOST SIMILAR EXAMPLES:")
        print("=" * 60)
        for idx, res in enumerate(results):
            print(f"{idx + 1}. ID: {res['id']} | Category: {res['category']} | Language: {res['language']}")
            print(f"   Similarity Score: {res['similarity_score']:.4f}")
            print(f"   Tags: {res['tags']}")
            print(f"   Explanation: {res['explanation']}")
            print(f"   Code Snippet:\n{res['code_snippet']}")
            print("-" * 60)

    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")

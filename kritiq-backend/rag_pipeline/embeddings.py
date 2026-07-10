import time
from google.genai.errors import ClientError
from ai_agent.gemini_client import client


def get_embedding(text: str) -> list[float]:
    """
    Generates a high-dimensional text embedding vector using the gemini-embedding-2 model.
    """
    start_time = time.perf_counter()
    try:
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=text
        )
        # Extract vector values
        values = response.embeddings[0].values
        return values
    except ClientError as e:
        print(f"Gemini Embedding API error: {e}")
        raise RuntimeError(f"Gemini Embedding API error: {e}") from e
    except Exception as e:
        print(f"Unexpected error generating embedding: {e}")
        raise RuntimeError(f"An unexpected error occurred during embedding: {e}") from e
    finally:
        duration = time.perf_counter() - start_time
        print(f"Embedding call took {duration:.2f} seconds")


if __name__ == "__main__":
    # Quick test run
    try:
        vector = get_embedding("Testing the RAG embedding generation pipeline.")
        print(f"Success! Vector length: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
    except Exception as e:
        print(f"Test failed: {e}")

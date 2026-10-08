import os
import time
from dotenv import load_dotenv
from groq import Groq
from groq import GroqError

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")

client = None
if API_KEY:
    try:
        client = Groq(api_key=API_KEY, timeout=30.0)
    except Exception as _client_err:
        print(
            f"[groq_client] Could not configure Groq client at import: "
            f"{_client_err}. ask_groq() will raise at call time."
        )
        client = None


def ask_groq(prompt: str, response_format: str = "text") -> str:
    """
    Calls Groq API.

    response_format:
        - "text" -> normal text/code output, used by Translation
        - "json" -> JSON output, used by Code Review
    """
    start_time = time.perf_counter()

    try:
        if client is None:
            raise RuntimeError(
                "GROQ_API_KEY is not configured in the environment."
            )

        request_kwargs = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "model": "openai/gpt-oss-120b",
        }

        # Only force JSON when the caller actually needs JSON.
        if response_format == "json":
            request_kwargs["response_format"] = {
                "type": "json_object"
            }

        chat_completion = client.chat.completions.create(
            **request_kwargs
        )

        content = chat_completion.choices[0].message.content

        if content is None:
            return ""

        return content

    except GroqError as e:
        print(f"Groq API error: {e}")
        raise RuntimeError(
            f"Groq API error occurred: {e}"
        ) from e

    except Exception as e:
        print(f"Unexpected error in Groq call: {e}")
        raise RuntimeError(
            f"An unexpected error occurred while calling Groq: {e}"
        ) from e

    finally:
        duration = time.perf_counter() - start_time
        print(f"Groq call took {duration:.2f} seconds")


if __name__ == "__main__":
    try:
        res = ask_groq(
            "Hello! Write a 1-sentence test message.",
            response_format="text"
        )
        print(f"Response: {res}")
    except Exception as e:
        print(f"Error: {e}")
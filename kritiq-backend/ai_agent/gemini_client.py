import os
import time
from dotenv import load_dotenv
import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

# Configure the client with a 30-second (30,000 milliseconds) request timeout
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=30_000)
)


def ask_gemini(prompt: str) -> str:
    start_time = time.perf_counter()
    gemini_failed = False
    gemini_error = None

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except httpx.TimeoutException as e:
        raise TimeoutError("The request to Gemini API timed out after 30 seconds.") from e
    except APIError as e:
        if e.code in (429, 503):
            gemini_failed = True
            gemini_error = e
        else:
            print(f"Gemini API error: {e}")
            raise
    finally:
        duration = time.perf_counter() - start_time
        print(f"Gemini call took {duration:.2f} seconds")

    if gemini_failed and gemini_error:
        print(f"[FALLBACK] Gemini unavailable (quota/overload) — retrying with Groq...")
        from ai_agent.groq_client import ask_groq
        groq_start_time = time.perf_counter()
        try:
            result = ask_groq(prompt)
            return result
        except Exception as groq_err:
            raise RuntimeError(
                f"Both primary (Gemini) and fallback (Groq) services failed.\n"
                f"Gemini Error: {gemini_error}\n"
                f"Groq Error: {groq_err}"
            ) from groq_err
        finally:
            groq_duration = time.perf_counter() - groq_start_time
            print(f"Groq fallback call took {groq_duration:.2f} seconds")



if __name__ == "__main__":
    from ai_agent.prompts.review_prompt import build_review_prompt

    hardcoded_code = """
def add(a, b):
    return a+b
"""

    prompt = build_review_prompt(hardcoded_code, language="python")
    print(ask_gemini(prompt))
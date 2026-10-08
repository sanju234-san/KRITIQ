import os
import time
from dotenv import load_dotenv
import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure client lazily — don't crash the whole backend at import time
# just because GEMINI_API_KEY isn't set yet.  ask_gemini() below will raise
# a clean RuntimeError when actually invoked without a key, so auth/OAuth
# routes and the test suite still run locally.
client = None
if API_KEY:
    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(timeout=30_000)
        )
    except Exception as _client_err:
        print(f"[gemini_client] Could not configure genai.Client at import: {_client_err}.  ask_gemini() will fall back to Groq at runtime.")
        client = None


def ask_gemini(prompt: str) -> str:
    """
    Executes prompt against Gemini 2.5 Flash.
    On timeout, 429, 503, 504, or any Gemini API failure,
    logs the fallback message and delegates to Groq Llama-3.
    """
    start_time = time.perf_counter()
    gemini_failed = False
    gemini_error = None

    try:
        if client is None:
            gemini_failed = True
            gemini_error = RuntimeError("GEMINI_API_KEY is not configured — falling back to Groq.")
        else:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return response.text
    except (httpx.TimeoutException, TimeoutError) as e:
        gemini_failed = True
        gemini_error = e
    except APIError as e:
        gemini_failed = True
        gemini_error = e
    except Exception as e:
        gemini_failed = True
        gemini_error = e
    finally:
        duration = time.perf_counter() - start_time
        print(f"Gemini call took {duration:.2f} seconds")

    if gemini_failed and gemini_error:
        print("[Gemini timeout] Switching to Groq Llama-3 fallback...")
        from ai_agent.groq_client import ask_groq
        groq_start_time = time.perf_counter()
        try:
            result = ask_groq(prompt)
            return result
        except Exception as groq_err:
            raise RuntimeError(
                f"Both primary (Gemini) and fallback (Groq) services failed: {groq_err}"
            ) from groq_err
        finally:
            groq_duration = time.perf_counter() - groq_start_time
            print(f"Groq fallback call took {groq_duration:.2f} seconds")
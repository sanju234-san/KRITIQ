import os
import time
from dotenv import load_dotenv
import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

# Configure client
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=30_000)
)


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
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
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
import os
import time
from dotenv import load_dotenv
import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure client lazily so the backend can start even when
# GEMINI_API_KEY is not configured locally.
client = None

if API_KEY:
    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(timeout=30_000)
        )
    except Exception as _client_err:
        print(
            f"[gemini_client] Could not configure genai.Client at import: "
            f"{_client_err}. ask_gemini() will fall back to Groq at runtime."
        )
        client = None


def ask_gemini(prompt: str, response_format: str = "text") -> str:
    """
    Executes the prompt against Gemini 2.5 Flash.

    response_format:
        - "text" -> normal text/code output, used by Translation
        - "json" -> JSON output, used by Code Review

    If Gemini fails, the same response format is passed to Groq fallback.
    """

    start_time = time.perf_counter()
    gemini_failed = False
    gemini_error = None

    try:
        if client is None:
            gemini_failed = True
            gemini_error = RuntimeError(
                "GEMINI_API_KEY is not configured — falling back to Groq."
            )

        else:
            # JSON mode is used only when the caller explicitly requests it.
            if response_format == "json":
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

            # Normal text mode for Translation and other text/code tasks.
            else:
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

    # ---------------------------------------------------------
    # Gemini failed -> Groq fallback
    # ---------------------------------------------------------
    if gemini_failed and gemini_error:
        print(
            f"[Gemini failed] Switching to Groq fallback... "
            f"Reason: {gemini_error}"
        )

        from ai_agent.groq_client import ask_groq

        groq_start_time = time.perf_counter()

        try:
            # IMPORTANT:
            # Preserve the requested response format.
            #
            # Translation:
            #     Gemini text -> Groq text
            #
            # Code Review:
            #     Gemini JSON -> Groq JSON
            result = ask_groq(
                prompt,
                response_format=response_format
            )

            return result

        except Exception as groq_err:
            raise RuntimeError(
                f"Both primary (Gemini) and fallback (Groq) services failed: "
                f"{groq_err}"
            ) from groq_err

        finally:
            groq_duration = time.perf_counter() - groq_start_time
            print(
                f"Groq fallback call took "
                f"{groq_duration:.2f} seconds"
            )
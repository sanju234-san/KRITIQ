# SANJEEVNI MODULE WALKTHROUGH
### A Complete Line-by-Line Annotation of Every File in the Sanjeevni Domain

> **How to read this document:** Each file section pastes the real source code in small logical chunks, immediately followed by a plain-English blockquote explaining exactly what that chunk does and *why* it is written that way. Nothing is skipped. This document was written by reading the code, not by executing it — no API calls were made during its generation.

---

## Table of Contents
1. [ai_agent/gemini_client.py](#1-ai_agentgemini_clientpy)
2. [ai_agent/groq_client.py](#2-ai_agentgroq_clientpy)
3. [ai_agent/review_service.py](#3-ai_agentreview_servicepy)
4. [ai_agent/translation_service.py](#4-ai_agenttranslation_servicepy)
5. [ai_agent/explanation_service.py](#5-ai_agentexplanation_servicepy)
6. [ai_agent/multi_agent_review.py](#6-ai_agentmulti_agent_reviewpy)
7. [ai_agent/walkthrough_writer.py](#7-ai_agentwalkthrough_writerpy)
8. [ai_agent/prompts/review_prompt.py](#8-ai_agentpromptsreview_promptpy)
9. [ai_agent/prompts/translation_prompt.py](#9-ai_agentpromststranslation_promptpy)
10. [ai_agent/prompts/explanation_prompt.py](#10-ai_agentpromptsexplanation_promptpy)
11. [ai_agent/prompts/multi_agent_prompts.py](#11-ai_agentpromptsmulti_agent_promptspy)
12. [cli/commands/review.py](#12-clicommandsreviewpy)
13. [cli/commands/translate.py](#13-clicommandstranslatepy)
14. [cli/commands/explain.py](#14-clicommandsexplainpy)
15. [cli/utils.py](#15-cliutilspy)
16. [mcp_server/server.py](#16-mcp_serverserverpy)
17. [mcp_server/tools.py](#17-mcp_servertoolspy)
18. [rag_pipeline/embeddings.py](#18-rag_pipelineembeddingspy)
19. [rag_pipeline/retriever.py](#19-rag_pipelineretrieverpy)
20. [repo_integration/github_api.py](#20-repo_integrationgithub_apipy)
21. [dataset/schema.py](#21-datasetschemapy)
22. [dataset/build_dataset.py](#22-datasetbuild_datasetpy)

---

## 1. `ai_agent/gemini_client.py`

**Purpose:** The single entry-point for all calls to the Google Gemini AI API; it configures the client, defines the `ask_gemini()` function used by every service, and implements automatic fallback to Groq when Gemini is unavailable.

---

```python
import os
```
> Imports Python's built-in `os` module. It is used one line later to read the `GEMINI_API_KEY` environment variable with `os.environ.get(...)`.

```python
import time
```
> Imports Python's built-in `time` module, specifically for `time.perf_counter()` — a high-resolution timer used to measure how long each API call takes and print that duration to the terminal.

```python
from dotenv import load_dotenv
```
> Imports the `load_dotenv` function from the third-party `python-dotenv` package. This function reads a `.env` file from the project root and injects its key-value pairs into the process environment, making them accessible via `os.environ.get(...)`.

```python
import httpx
```
> Imports the `httpx` library, which is the underlying HTTP client used internally by the Google Gemini SDK. We import it here specifically so we can catch `httpx.TimeoutException` — a timeout error that bubbles up from deep inside the SDK rather than being wrapped in a Gemini-specific error type.

```python
from google import genai
```
> Imports the top-level `genai` namespace from Google's `google-generativeai` SDK. The `genai.Client` class (used below) is the main entry-point for interacting with Gemini models.

```python
from google.genai import types
```
> Imports the `types` sub-module, which contains configuration classes. We use `types.HttpOptions` below to set a custom request timeout on the client.

```python
from google.genai.errors import APIError, ClientError
```
> Imports two specific error types from the Gemini SDK. `APIError` is the base class for server-side errors (like rate limit 429 or overload 503). `ClientError` is for errors on the embedding side. We catch `APIError` specifically in `ask_gemini()` to decide whether to fall back to Groq.

```python
load_dotenv()
```
> Calls the function imported above. At module load time (the moment any other file does `from ai_agent.gemini_client import ...`), this runs and reads `.env`, ensuring `GEMINI_API_KEY` is available in the environment before the next line tries to read it.

```python
API_KEY = os.environ.get("GEMINI_API_KEY")
```
> Reads the `GEMINI_API_KEY` value from the environment. `os.environ.get(...)` returns `None` if the key is not set, rather than raising a `KeyError` like `os.environ[...]` would.

```python
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")
```
> Guards against running without a key. If `API_KEY` is `None` or an empty string (both falsy), we raise a `ValueError` immediately with a helpful message. This happens at import time, so the error surfaces the moment the application starts — not buried in a later API call.

```python
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=30_000)
)
```
> Creates the Gemini client object that all subsequent API calls use. `api_key=API_KEY` authenticates the requests. `http_options=types.HttpOptions(timeout=30_000)` sets a 30-second (30,000 ms) hard timeout on every network request — without this, a stalled API call would hang the CLI indefinitely. The `30_000` uses an underscore digit separator for readability (PEP 515).

---

```python
def ask_gemini(prompt: str) -> str:
```
> Defines the public function that all other files in the system call to get a text response from Gemini. It takes a single `prompt` string (the fully-assembled text instruction) and returns Gemini's plain-text reply as a string.

```python
    start_time = time.perf_counter()
```
> Records the exact moment the function starts, using the highest-resolution timer available. This is stored so we can subtract it later in `finally:` to compute elapsed time.

```python
    gemini_failed = False
    gemini_error = None
```
> Sets up two "flag" variables before the try block. Python's scoping rules mean variables declared inside a `try` block are not accessible in code that runs after the `finally` block. These flags let us communicate the failure state from inside `except` to the code block that runs after `finally`.

```python
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
```
> The main API call. `client.models.generate_content(...)` sends the prompt to the `gemini-2.5-flash` model and waits for a response. `response.text` extracts the plain text from the response object and immediately returns it. If this line succeeds, the function exits here and the rest of the function does not run.

```python
    except httpx.TimeoutException as e:
        raise TimeoutError("The request to Gemini API timed out after 30 seconds.") from e
```
> Catches the specific exception that fires when the 30-second timeout we configured is exceeded. We re-raise it as Python's built-in `TimeoutError` with a clear human-readable message. The `from e` clause chains the original exception so the full traceback is preserved for debugging.

```python
    except APIError as e:
        if e.code in (429, 503):
            gemini_failed = True
            gemini_error = e
        else:
            print(f"Gemini API error: {e}")
            raise
```
> Catches Gemini server-side errors. HTTP 429 means "too many requests" (rate limit exceeded) and 503 means "service unavailable" (overloaded). For these two specific codes, we set the flag variables and let the code continue — we will try Groq next. For any other error code (like 400 bad request or 401 unauthorized), we print the error and re-raise it, because those are not recoverable by switching models.

```python
    finally:
        duration = time.perf_counter() - start_time
        print(f"Gemini call took {duration:.2f} seconds")
```
> The `finally` block runs regardless of whether the `try` succeeded or an exception was caught. It calculates elapsed time by subtracting `start_time` from the current timestamp, then prints it. The `:.2f` format specifier rounds the float to 2 decimal places.

```python
    if gemini_failed and gemini_error:
        print(f"[FALLBACK] Gemini unavailable (quota/overload) — retrying with Groq...")
        from ai_agent.groq_client import ask_groq
```
> After the `finally` block completes, if our flag is set, we enter the fallback path. The import is intentionally placed *inside* the function rather than at the top of the file. This is a deliberate design choice: it avoids a circular import (groq_client also indirectly references this module) and prevents Groq from being imported at all when Gemini works fine.

```python
        groq_start_time = time.perf_counter()
        try:
            result = ask_groq(prompt)
            return result
```
> Starts a new timer for the Groq call, then calls `ask_groq` with the exact same prompt. If Groq succeeds, we return its result. The caller never knows whether the response came from Gemini or Groq — the interface is identical.

```python
        except Exception as groq_err:
            raise RuntimeError(
                f"Both primary (Gemini) and fallback (Groq) services failed.\n"
                f"Gemini Error: {gemini_error}\n"
                f"Groq Error: {groq_err}"
            ) from groq_err
```
> If Groq also fails, we raise a `RuntimeError` that includes the error messages from both services. This gives the developer a complete picture of what went wrong on both sides, instead of just seeing the Groq error with no mention of the Gemini failure that triggered the fallback.

```python
        finally:
            groq_duration = time.perf_counter() - groq_start_time
            print(f"Groq fallback call took {groq_duration:.2f} seconds")
```
> Same pattern as the Gemini timer — a `finally` block that always prints the duration of the Groq call, whether it succeeded or failed.

```python
if __name__ == "__main__":
    from ai_agent.prompts.review_prompt import build_review_prompt

    hardcoded_code = """
def add(a, b):
    return a+b
"""
    prompt = build_review_prompt(hardcoded_code, language="python")
    print(ask_gemini(prompt))
```
> This block only runs when you execute the file directly (`python ai_agent/gemini_client.py`), not when it is imported by another module. It's a quick manual smoke-test: build a review prompt for a tiny add function and print Gemini's response, confirming the client is wired up correctly.

---

## 2. `ai_agent/groq_client.py`

**Purpose:** Configures and exposes the Groq AI API client as a fallback model when Gemini is unavailable; provides the `ask_groq()` function called by `gemini_client.py`.

---

```python
import os
import time
from dotenv import load_dotenv
```
> Same three imports as `gemini_client.py` — `os` for environment variable access, `time` for measuring call duration, and `load_dotenv` for reading the `.env` file.

```python
from groq import Groq
from groq import GroqError
```
> Imports the `Groq` client class (used to make API calls) and `GroqError` (the base exception class for all Groq-specific errors) from the official `groq` Python SDK.

```python
load_dotenv()
```
> Reads the `.env` file into the environment. Even though `gemini_client.py` also calls this, it is safe to call `load_dotenv()` multiple times — subsequent calls are no-ops if the environment is already populated.

```python
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")
```
> Reads the `GROQ_API_KEY` from the environment. If it's missing, raises an error immediately at import time — the same fail-fast pattern used in `gemini_client.py`.

```python
client = Groq(
    api_key=API_KEY,
    timeout=30.0  # 30 seconds request timeout
)
```
> Creates the Groq client with authentication and a 30-second timeout. Note that Groq's SDK takes `timeout` in seconds as a plain float, while Gemini's took milliseconds as an integer — this is a SDK API difference worth remembering.

---

```python
def ask_groq(prompt: str) -> str:
    """
    Calls Groq API with the provided prompt using llama-3.3-70b-versatile.
    """
```
> Defines the fallback function. The docstring documents which model is used — `llama-3.3-70b-versatile` is a large, capable open-source language model hosted on Groq's infrastructure.

```python
    start_time = time.perf_counter()
```
> Records the start time for duration measurement, identical to the pattern in `gemini_client.py`.

```python
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
```
> Makes the API call using the OpenAI-compatible "chat completions" interface. Groq uses the same message format as OpenAI: a list of message dictionaries, each with a `role` ("user", "assistant", or "system") and `content` (the text). We send a single user message containing the full prompt.

```python
        content = chat_completion.choices[0].message.content
        if content is None:
            return ""
        return content
```
> Extracts the text from the response. `choices[0]` gets the first (and only) completion choice. `.message.content` gets the text of the assistant's response. We guard against `None` — the API can technically return no content in edge cases — and return an empty string rather than crashing.

```python
    except GroqError as e:
        print(f"Groq API error: {e}")
        raise RuntimeError(f"Groq API error occurred: {e}") from e
    except Exception as e:
        print(f"Unexpected error in Groq call: {e}")
        raise RuntimeError(f"An unexpected error occurred while calling Groq: {e}") from e
```
> Two exception handlers: the first catches Groq-specific errors (authentication failure, model not found, etc.), the second catches any other unexpected error (network issues, parsing failures). Both print a message and re-raise as `RuntimeError` so the calling code in `gemini_client.py` can catch it and compose the "both services failed" error message.

```python
    finally:
        duration = time.perf_counter() - start_time
        print(f"Groq call took {duration:.2f} seconds")
```
> Always prints the duration of the Groq call. This fires even if an exception was raised, giving you timing information even on failures.

```python
if __name__ == "__main__":
    # Small test block
    try:
        res = ask_groq("Hello! Write a 1-sentence test message.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Error: {e}")
```
> Manual smoke-test block. When run directly, sends a trivial one-sentence prompt to Groq and prints the result, confirming the API key and client are working.

---

## 3. `ai_agent/review_service.py`

**Purpose:** Orchestrates a complete code review request by gathering MCP project context, retrieving RAG examples, assembling the final prompt, and calling Gemini — all exposed through the single `review_code()` function.

---

```python
import os
from ai_agent.prompts.review_prompt import build_review_prompt
from ai_agent.gemini_client import ask_gemini
```
> Imports `os` for directory path manipulation. Imports `build_review_prompt` — the function that assembles the text prompt from all the inputs. Imports `ask_gemini` — the function that sends the assembled prompt to Gemini and returns its response.

```python
def review_code(code: str, language: str = "python", file_path: str = None) -> str:
```
> Defines the main function. `code` is the raw source code to review. `language` defaults to `"python"` if not specified (for example, when called from a test). `file_path` is optional — if provided, the function uses it to find sibling files for project context.

```python
    retrieved_examples = None
    project_context = None
```
> Initialises both enrichment variables to `None`. This is important because both are passed into `build_review_prompt` at the end — if either enrichment step fails, we want to pass `None` (no enrichment) rather than a partially-built or corrupt value.

```python
    if file_path:
        try:
            from mcp_server.tools import list_local_files
```
> Only attempts MCP context gathering if a `file_path` was provided. The import is inside the `try` block so that if `mcp_server` is unavailable for any reason, we catch the import error the same as any other exception. This is a defensive pattern — the MCP context is nice-to-have, not required.

```python
            directory = os.path.dirname(file_path) or "."
```
> Gets the directory containing the file. `os.path.dirname("test_sample.py")` returns `""` (empty string) because there's no directory prefix. The `or "."` converts that empty string to `"."` (the current directory), so `list_local_files` always receives a valid path.

```python
            sibling_files = list_local_files(directory)
```
> Calls our MCP tool to get a list of all filenames in the same directory as the file being reviewed.

```python
            if sibling_files and not any(f.startswith("Error:") for f in sibling_files):
```
> A double guard: first checks the list is non-empty, then checks that no item in the list starts with `"Error:"`. The `list_local_files` function returns error strings in the list rather than raising exceptions (e.g. `["Error: Directory does not exist."]`), so this pattern detects that failure mode without needing a try-catch.

```python
                basename = os.path.basename(file_path)
                project_context = [f for f in sibling_files if f != basename]
```
> Gets just the filename (without the directory) of the file being reviewed, then builds `project_context` as a list of all sibling files *excluding* the reviewed file itself. Including the file's own name in "project context" would be misleading — the context is meant to represent what else exists around it.

```python
                if project_context:
                    print(f"[MCP] Found {len(project_context)} sibling files for project context.")
                else:
                    project_context = None
```
> If after filtering the list is still non-empty, prints a status message and keeps it. If the file was the only thing in the directory (context list is empty after removing self), resets to `None` so the prompt builder knows there's nothing to include.

```python
        except Exception as e:
            print(f"[MCP WARNING] Could not gather project context — skipping. Reason: {e}")
            project_context = None
```
> Catches any exception from the entire MCP block — import errors, OS errors, anything — prints a non-fatal warning, and resets `project_context` to `None`. The review will still run, just without the project context enrichment.

```python
    try:
        from rag_pipeline.retriever import get_or_build_combined_embeddings, retrieve_similar_examples

        dataset_with_embeddings = get_or_build_combined_embeddings()
        retrieved_examples = retrieve_similar_examples(code, dataset_with_embeddings, top_k=2)
        print(f"[RAG] Retrieved {len(retrieved_examples)} reference examples for review prompt.")
    except Exception as e:
        print(f"[RAG WARNING] Could not retrieve examples — falling back to plain prompt. Reason: {e}")
        retrieved_examples = None
```
> The RAG enrichment block. Loads all 72 dataset entries (from cache if available), then finds the 2 entries most semantically similar to the code being reviewed, using embedding cosine similarity. If anything goes wrong (no API key for embeddings, cache corrupted, etc.), warns and falls back gracefully — the review will continue without examples.

```python
    prompt = build_review_prompt(code, language, retrieved_examples=retrieved_examples, project_context=project_context)
    return ask_gemini(prompt)
```
> Assembles the final prompt by passing the code, language, and any enrichment data into the prompt builder, then sends it to Gemini and returns the raw text response. This is the only line that is guaranteed to always run — everything above was optional enrichment.

---

## 4. `ai_agent/translation_service.py`

**Purpose:** Mirrors `review_service.py` exactly but for the translate workflow — gathers MCP context and RAG examples, builds a translation prompt, and returns Gemini's translated code.

---

```python
import os
from ai_agent.prompts.translation_prompt import build_translation_prompt
from ai_agent.gemini_client import ask_gemini
```
> Same pattern as `review_service.py` but importing the translation-specific prompt builder instead of the review one.

```python
def translate_code(code: str, source_language: str, target_language: str, file_path: str = None) -> str:
```
> The main function. Takes the source `code`, the language it's currently written in (`source_language`), the language to convert it to (`target_language`), and an optional `file_path` for MCP context.

```python
    retrieved_examples = None
    project_context = None
```
> Same defensive initialisation as in `review_service.py`.

```python
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
```
> Identical MCP block to `review_service.py`. In the translation context, the sibling file list tells Gemini what conventions or naming patterns exist in the surrounding project, which it can consider when choosing how to name things in the translated output.

```python
    try:
        from rag_pipeline.retriever import get_or_build_combined_embeddings, retrieve_similar_examples
        dataset_with_embeddings = get_or_build_combined_embeddings()
        retrieved_examples = retrieve_similar_examples(code, dataset_with_embeddings, top_k=2)
        print(f"[RAG] Retrieved {len(retrieved_examples)} reference examples for translation prompt.")
    except Exception as e:
        print(f"[RAG WARNING] Could not retrieve examples — falling back to plain prompt. Reason: {e}")
        retrieved_examples = None
```
> Identical RAG block. The 2 most similar dataset entries are retrieved and will be passed into the translation prompt as "reference examples of common issues" — giving Gemini context about what kinds of patterns exist in this codebase.

```python
    prompt = build_translation_prompt(
        code, source_language, target_language,
        retrieved_examples=retrieved_examples,
        project_context=project_context
    )
    return ask_gemini(prompt)
```
> Assembles the translation prompt with all 4 inputs (the code, both language names, and the two optional enrichments) and sends it to Gemini. Note `translate_code` takes *three* required arguments vs `review_code`'s two — the target language is extra information unique to translation.

---

## 5. `ai_agent/explanation_service.py`

**Purpose:** Mirrors `review_service.py` and `translation_service.py` for the explain workflow — gathers context, builds an explanation prompt, and returns Gemini's plain-language description of the code.

---

```python
import os
from ai_agent.prompts.explanation_prompt import build_explanation_prompt
from ai_agent.gemini_client import ask_gemini
```
> Same trio of imports, this time pulling in the explanation-specific prompt builder.

```python
def explain_code(code: str, language: str = "python", file_path: str = None) -> str:
```
> Same signature shape as `review_code` — takes code, an optional language (defaults to Python), and an optional file path. Unlike `translate_code`, there is no `target_language` because explanation doesn't need a target language.

```python
    retrieved_examples = None
    project_context = None
```
> Same defensive initialisation.

```python
    # MCP block (identical pattern)
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
```
> The identical MCP context block. In the explanation context, the sibling file list helps Gemini tell the person *where this code fits in the project* — for example, mentioning that `greet.py` lives alongside `playground.py` and `cli/` adds useful framing.

```python
    # RAG block (identical pattern)
    try:
        from rag_pipeline.retriever import get_or_build_combined_embeddings, retrieve_similar_examples
        dataset_with_embeddings = get_or_build_combined_embeddings()
        retrieved_examples = retrieve_similar_examples(code, dataset_with_embeddings, top_k=2)
        print(f"[RAG] Retrieved {len(retrieved_examples)} reference examples for explanation prompt.")
    except Exception as e:
        print(f"[RAG WARNING] Could not retrieve examples — falling back to plain prompt. Reason: {e}")
        retrieved_examples = None
```
> Identical RAG block — the 2 most similar examples give Gemini context about what similar code is meant to do, helping it calibrate the level of explanation.

```python
    prompt = build_explanation_prompt(
        code, language,
        retrieved_examples=retrieved_examples,
        project_context=project_context
    )
    return ask_gemini(prompt)
```
> Builds the explanation prompt with the code, language, and enrichments, then calls Gemini. This is the only line guaranteed to always run — the enrichment above is all best-effort.

---

## 6. `ai_agent/multi_agent_review.py`

**Purpose:** Implements a two-agent "reviewer + verifier" workflow where Gemini identifies potential issues and Groq independently confirms them, reducing false positives.

---

```python
from ai_agent.gemini_client import ask_gemini
from ai_agent.groq_client import ask_groq
from ai_agent.prompts.multi_agent_prompts import build_reviewer_prompt, build_verifier_prompt
```
> Imports both AI clients (Gemini for Agent 1 / Reviewer, Groq for Agent 2 / Verifier) and both prompt builders. Unlike the service files, this module calls Groq *directly by design* — not as a fallback, but as a deliberate second independent agent.

```python
def multi_agent_review(code: str, language: str = "python") -> str:
    """
    Runs a two-agent code review workflow:
    1. Agent 1 (Reviewer - Gemini) identifies potential issues in the code.
    2. Agent 2 (Verifier - Groq) verifies these issues against the original code
       and returns only the confirmed issues.

    Note: This process executes 1 Gemini API call and 1 Groq API call.
    """
```
> The docstring explicitly states the API cost: exactly 1 Gemini call and 1 Groq call. This is important for users to know since it consumes quota from two separate services.

```python
    print(f"\n--- Initiating Multi-Agent Code Review ({language}) ---")
    print("[Agent 1] Reviewer (Gemini) is analyzing the code...")
```
> Prints status messages to keep the user informed during what will be a multi-step operation. The `\n` at the start adds a blank line to visually separate this from any preceding output.

```python
    reviewer_prompt = build_reviewer_prompt(code, language)
    reviewer_issues = ask_gemini(reviewer_prompt)
```
> Step 1: builds the reviewer prompt (instructing Gemini to list short 1-2 sentence issues) and calls Gemini. The result (`reviewer_issues`) is a raw text string — a simple bullet list of potential problems Gemini found.

```python
    print("\n[Agent 1] Reviewer findings:")
    print(reviewer_issues)
```
> Prints Gemini's raw findings to the terminal so the user can see what Agent 1 found before Agent 2 filters it.

```python
    print("\n[Agent 2] Verifier (Groq) is checking the findings...")
```
> Status message before the second API call.

```python
    verifier_prompt = build_verifier_prompt(code, language, reviewer_issues)
    verified_issues = ask_groq(verifier_prompt)
```
> Step 2: builds the verifier prompt by passing in the *original code*, the language, AND the `reviewer_issues` text. Groq sees both the code and Gemini's findings, allowing it to independently verify each issue against the actual source. The result is a filtered list with only confirmed issues.

```python
    print("--- Multi-Agent Code Review Finished ---\n")
    return verified_issues
```
> Prints a closing status line and returns only the verified issues — not Gemini's raw list, but Groq's confirmed subset.

```python
if __name__ == "__main__":
    SAMPLE_CODE = """\
def calculate_discount(price, discount_percent):
    unused_var = "debug"
    discount_amount = price * discount_percent / 100
    discounted = price - discount_amount
    # missing return statement
"""
    print("Testing multi_agent_review with a hardcoded sample snippet...")
    result = multi_agent_review(SAMPLE_CODE, "python")
    print("=" * 60)
    print("FINAL VERIFIED ISSUES:")
    print("=" * 60)
    print(result)
```
> A self-contained test block. The sample code deliberately has two obvious issues: an unused variable (`unused_var`) and a missing `return` statement. Running this directly lets you verify the full two-agent pipeline works end-to-end.

---

## 7. `ai_agent/walkthrough_writer.py`

**Purpose:** Generates rich Markdown walkthrough files from AI review, translation, and explanation outputs, saving them to the `walkthroughs/` directory.

---

```python
import os
import re
from datetime import datetime
```
> `os` for directory creation and path manipulation. `re` (regular expressions) for parsing the structured text returned by Gemini's review. `datetime` for generating a human-readable timestamp to embed in each walkthrough file.

```python
def parse_review_result(review_result: str):
    """
    Parses Gemini's review result to extract the summary and list of numbered issues.
    """
    summary = ""
    issues = []
```
> Defines a helper function that takes Gemini's raw review text and splits it into two parts: a `summary` string and an `issues` list of `(number, content)` tuples. Initialises both to empty/falsy values.

```python
    lines = review_result.splitlines()
```
> Splits the entire review text into a list of individual lines, which is easier to scan for headers than the raw multi-line string.

```python
    issues_header_index = -1
    summary_header_index = -1

    for i, line in enumerate(lines):
        if re.match(r'(?i)^\s*summary\s*:', line):
            summary_header_index = i
        elif re.match(r'(?i)^\s*issues\s*:', line):
            issues_header_index = i
```
> Scans every line looking for the "Summary:" and "Issues:" headers that the review prompt instructs Gemini to produce. `(?i)` makes the match case-insensitive, `^\s*` allows any leading whitespace, and `\s*:` allows space before the colon. We record the line index rather than the content.

```python
    if summary_header_index != -1:
        summary_end = issues_header_index if issues_header_index != -1 else len(lines)
        summary_lines = lines[summary_header_index + 1 : summary_end]
        first_line = lines[summary_header_index]
        summary_first_part = re.sub(r'(?i)^\s*summary\s*:\s*', '', first_line).strip()
        summary_rest = "\n".join(summary_lines).strip()
        summary = (summary_first_part + "\n" + summary_rest).strip() if summary_first_part else summary_rest
```
> Extracts the summary text. `summary_end` is set to either the start of the Issues section (if found) or the end of the document. The text from the Summary header line itself (after removing "Summary:") is captured as `summary_first_part`, and all subsequent lines until the Issues header become `summary_rest`. Both are joined into the final `summary` string.

```python
    else:
        if issues_header_index != -1 and issues_header_index > 0:
            summary = "\n".join(lines[:issues_header_index]).strip()
            summary = re.sub(r'(?i)^\s*summary\s*:\s*', '', summary).strip()
```
> Fallback: if the explicit "Summary:" header wasn't found but "Issues:" was, everything before the Issues section is treated as the summary. This handles cases where Gemini doesn't use the exact header word.

```python
    if issues_header_index != -1:
        issues_text = "\n".join(lines[issues_header_index + 1 :])
        parts = re.split(r'\n\s*(\d+)\.\s+', '\n' + issues_text)
        if len(parts) > 1:
            for idx in range(1, len(parts), 2):
                num = parts[idx]
                content = parts[idx+1].strip() if idx+1 < len(parts) else ""
                if content:
                    issues.append((num, content))
```
> Extracts individual numbered issues. The regex `\n\s*(\d+)\.\s+` splits on patterns like "1. " or " 2. " at the start of a line. `re.split` with a capturing group `(\d+)` returns the split text interleaved with the captured groups — so `parts[1]` is the issue number, `parts[2]` is the issue content, etc., stepping by 2.

```python
    if not issues:
        parts = re.split(r'\n\s*(\d+)\.\s+', '\n' + review_result)
        if len(parts) > 1:
            for idx in range(1, len(parts), 2):
                num = parts[idx]
                content = parts[idx+1].strip() if idx+1 < len(parts) else ""
                if content:
                    issues.append((num, content))
```
> Final fallback: if no issues were found under an "Issues:" header, searches the entire raw review text for numbered list items. This handles non-standard Gemini responses.

```python
    return summary.strip(), issues
```
> Returns the extracted summary string and the list of `(number, content)` tuples.

---

```python
def write_review_walkthrough(file_path: str, language: str, review_result: str, output_dir: str = "walkthroughs") -> str:
```
> Defines the public function called by `cli/commands/review.py`. Takes the reviewed file's path, its language, Gemini's raw review text, and an output directory (defaulting to `walkthroughs/`).

```python
    try:
        os.makedirs(output_dir, exist_ok=True)
```
> Creates the output directory if it doesn't already exist. `exist_ok=True` prevents an error if the directory is already there — without this flag, a `FileExistsError` would be raised on every run after the first.

```python
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_review.md"
        output_path = os.path.join(output_dir, output_filename)
```
> Computes all the path/name pieces: `timestamp` for the "Reviewed On" field, `filename` extracts just the file name (e.g. `test_sample.py`), `base_name` strips the extension (e.g. `test_sample`), and `output_filename` adds `_review.md`. `output_path` joins the directory and filename.

```python
        summary = ""
        issues = []
        try:
            summary, issues = parse_review_result(review_result)
        except Exception:
            summary = ""
            issues = []
```
> Calls `parse_review_result` inside its own try-except. If parsing fails for any reason, we silently fall back to empty values — the document will still be written, just with the raw review text instead of structured sections.

```python
        if summary:
            intro = summary
        else:
            intro = f"A code review of `{filename}` was performed using the AI agent."
```
> Determines the intro paragraph. If we extracted a summary, use it. Otherwise, generate a generic sentence.

```python
        issues_count = len(issues)
        if issues_count == 0:
            issues_count = len(re.findall(r'\n\s*\d+\.\s+', "\n" + review_result))
```
> Counts the issues. If the structured parser found none (`issues` list is empty), falls back to counting numbered list items (`1. `, `2. `, etc.) in the raw text, giving an approximate count.

```python
        if issues:
            parsed_issues_md = []
            for num, content in issues:
                first_line = content.splitlines()[0] if content else ""
                if " - " in first_line:
                    title, rest = first_line.split(" - ", 1)
                    ...
                elif ":" in first_line and len(first_line.split(":", 1)[0]) < 40:
                    title, rest = first_line.split(":", 1)
                    ...
                elif len(first_line) < 60:
                    title = first_line.strip()
                    body = "\n".join(content.splitlines()[1:])
                else:
                    title = "Issue Details"
                    body = content
```
> For each issue, tries to extract a short title from the first line using multiple heuristics: "Issue Title - explanation" format (split on ` - `), "Title: explanation" format (split on `:`), short first line as title, or a generic "Issue Details" fallback. This handles the variability in how Gemini formats its responses.

```python
                body = re.sub(r'(?i)\bexplanation\s*:', '**Explanation:**', body)
                body = re.sub(r'(?i)\bsuggested fix\s*:', '**Suggested Fix:**', body)
                body = re.sub(r'(?i)\brecommendation\s*:', '**Recommendation:**', body)
```
> Converts plain labels like "Explanation:" into bold Markdown labels like `**Explanation:**`, making the walkthrough document visually clearer when rendered.

```python
                parsed_issues_md.append(f"### {num}. {title}\n\n{body.strip()}")
            issues_identified = "\n\n".join(parsed_issues_md)
```
> Formats each issue as a `### 1. Title` heading with its body, then joins all formatted issues with double newlines into one big Markdown section.

```python
        else:
            formatted_result = re.sub(r'(?i)\bexplanation\s*:', '**Explanation:**', review_result)
            formatted_result = re.sub(r'(?i)\bsuggested fix\s*:', '**Suggested Fix:**', formatted_result)
            formatted_result = re.sub(r'(?i)\brecommendation\s*:', '**Recommendation:**', formatted_result)
            issues_identified = formatted_result
```
> Fallback for when no issues were parsed: use the entire raw review result, but still apply the bold-label substitutions. The document will have the raw AI output, formatted slightly for Markdown.

```python
        md_content = (
            f"# Walkthrough — Code Review: `{filename}`\n\n"
            f"{intro}\n\n"
            f"## 📋 Overview\n\n"
            f"| | |\n"
            f"|---|---|\n"
            f"| **File** | `{file_path}` |\n"
            f"| **Language** | {language} |\n"
            f"| **Reviewed On** | {timestamp} |\n"
            f"| **Issues Found** | {issues_count} |\n\n"
            f"## 🔍 Issues Identified\n\n"
            f"{issues_identified}\n\n"
            f"## ✅ Recommended Next Steps\n"
            f"- [ ] Review the recommendations and warning flags raised above.\n"
            f"- [ ] Implement the suggested optimizations or refactoring steps.\n"
            f"- [ ] Re-run the code review to verify improvements.\n\n"
            f"---\n"
            f"*Generated automatically by Kritiq's AI Review Agent — {timestamp}*\n"
        )
```
> Builds the complete Markdown document as a single string using concatenated f-strings. Each `f"..."` line is a separate string; Python automatically concatenates them when they are adjacent inside parentheses. This avoids triple-quoted strings, which can introduce unexpected indentation or leading whitespace.

```python
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
```
> Writes the document to disk. `encoding="utf-8"` ensures emoji characters (like 📋, 🔍, ✅) are stored correctly. Using a context manager (`with`) ensures the file is closed properly even if an error occurs during writing.

```python
        full_path = os.path.abspath(output_path)
        print(f"Code review walkthrough generated successfully: {full_path}")
        return full_path
    except Exception as e:
        raise RuntimeError(f"Failed to write review walkthrough: {e}")
```
> Converts the relative output path to an absolute path (so the user sees the complete filesystem location in the terminal), prints a success message, and returns the path. If anything in the entire `try` block failed, raises a `RuntimeError` with the reason — unlike `write_explanation_walkthrough`, this function raises rather than warns.

---

```python
def write_translation_walkthrough(file_path: str, source_language: str, target_language: str, translated_code: str, output_dir: str = "walkthroughs") -> str:
```
> The translation walkthrough function. Takes the file path, both language names, and the raw translated code (which will be embedded in a syntax-highlighted code block).

```python
        lang_tag = target_language.lower().strip()
        lang_mappings = {
            "python": "python", "py": "python",
            "javascript": "javascript", "js": "javascript",
            ...
        }
        lang_tag = lang_mappings.get(lang_tag, lang_tag)
```
> Normalises the target language name to the code fence tag that Markdown renderers recognise. For example, `"JavaScript"` becomes `"javascript"` (the correct fence tag), and `"c++"` becomes `"cpp"`. The `.get(lang_tag, lang_tag)` default means unknown languages fall through unchanged.

```python
        md_content = (
            f"# Walkthrough — Code Translation: `{filename}`\n\n"
            f"Translated `{filename}` from {source_language} to {target_language}.\n\n"
            ...
            f"## 💻 Translated Code\n\n"
            f"```{lang_tag}\n"
            f"{translated_code}\n"
            f"```\n\n"
            ...
        )
```
> Builds the translation walkthrough. The translated code is embedded inside a fenced code block with the correct language tag for syntax highlighting. The rest of the structure (Overview table, Next Steps, footer) mirrors the review walkthrough.

---

```python
def write_explanation_walkthrough(file_path: str, language: str, explanation_result: str, output_dir: str = "walkthroughs") -> str:
```
> The explanation walkthrough function — the newest addition, added today.

```python
        output_filename = f"{base_name}_explanation.md"
```
> Names the file `<basename>_explanation.md`, following the same `_review.md` / `_translation.md` convention.

```python
        md_content = (
            f"# Walkthrough — Code Explanation: `{filename}`\n\n"
            f"Explanation of `{filename}` ({language}).\n\n"
            f"## 📋 Overview\n\n"
            f"| | |\n"
            f"|---|---|\n"
            f"| **File** | `{file_path}` |\n"
            f"| **Language** | {language} |\n"
            f"| **Explained On** | {timestamp} |\n\n"
            f"## 💡 Explanation\n\n"
            f"{explanation_result}\n\n"
            f"## ✅ Recommended Next Steps\n"
            f"- [ ] Review this explanation to understand the code's purpose.\n"
            f"- [ ] Ask for clarification on any part that's still unclear.\n\n"
            f"---\n"
            f"*Generated automatically by Kritiq's AI Explanation Agent — {timestamp}*\n"
        )
```
> The explanation walkthrough embeds Gemini's full explanation text under `## 💡 Explanation` rather than parsing it into sub-sections, because explanation output is free-form prose rather than a structured issue list.

```python
    except Exception as e:
        print(f"Warning: Failed to write explanation walkthrough: {e}")
        return ""
```
> **Key difference** from the other two functions: instead of raising a `RuntimeError`, this catches any failure and prints a warning, then returns an empty string. This is intentional — a walkthrough write failure should never abort a running CLI command.

---

## 8. `ai_agent/prompts/review_prompt.py`

**Purpose:** Builds the exact text prompt that gets sent to Gemini for a code review, optionally including RAG reference examples and MCP project context.

---

```python
def build_review_prompt(code: str, language: str = "python", retrieved_examples: list[dict] = None, project_context: list[str] = None) -> str:
```
> The single function in this file. All four parameters are needed to build a complete prompt. `retrieved_examples` and `project_context` default to `None` so the function works correctly even when called without them.

```python
    reference_section = ""
    if retrieved_examples:
        reference_section = "\nReference Examples of Bad Practices:\n"
        for idx, example in enumerate(retrieved_examples):
            reference_section += f"\nExample {idx + 1}:\n"
            reference_section += f"Code Snippet:\n{example.get('code_snippet', '')}\n"
            reference_section += f"Explanation: {example.get('explanation', '')}\n"
            reference_section += "-" * 40 + "\n"
```
> Builds the optional RAG section. If `retrieved_examples` is provided (not `None` or empty), iterates over them with index numbers, extracting the `code_snippet` and `explanation` fields from each dict. The `.get(..., '')` pattern safely returns empty string if the key is missing rather than raising a `KeyError`. The `"-" * 40` is a visual separator line of 40 dashes.

```python
    context_section = ""
    if project_context:
        file_list = ", ".join(project_context)
        context_section = f"""
Project Context:
This file exists alongside these other files in the same project directory: {file_list}.
Consider whether this code might duplicate logic or violate conventions used elsewhere in the project, if relevant.
"""
```
> Builds the optional MCP section. Joins the list of sibling filenames into a comma-separated string and embeds it in a sentence that tells Gemini to consider cross-file concerns — duplicate logic, naming conventions, etc.

```python
    prompt = f"""
You are a careful, experienced code reviewer.
Review the following {language} code and identify any issues.

For each issue you find, provide:
- A short title for the issue
- An explanation of why it matters
- A suggested fix, if applicable
{reference_section}{context_section}
Structure your response as:
Summary: <a 1-2 sentence overview of the code's overall quality>
Issues:
1. <issue title> - <explanation and suggested fix>
2. <issue title> - <explanation and suggested fix>

Code:
{code}
"""
    return prompt.strip()
```
> Assembles the final prompt using an f-string triple-quoted block. The `{reference_section}` and `{context_section}` are injected inline — if either is an empty string, they contribute nothing to the prompt. `{language}` personalises the instruction. The `Structure your response as:` section tells Gemini the exact output format the parser in `walkthrough_writer.py` expects. `.strip()` removes leading/trailing whitespace from the entire assembled prompt.

---

## 9. `ai_agent/prompts/translation_prompt.py`

**Purpose:** Builds the exact text prompt for code translation, with strict instructions that ensure Gemini returns *only* raw translated code with no surrounding commentary.

---

```python
# Sanjeevni domain - Translation prompts
```
> A module-level comment identifying ownership and purpose. Comments like this help when navigating a large multi-module project.

```python
def build_translation_prompt(code: str, source_language: str, target_language: str, retrieved_examples: list[dict] = None, project_context: list[str] = None) -> str:
```
> Five parameters: the code to translate, both language names, and the two optional enrichment lists.

```python
    reference_section = ""
    if retrieved_examples:
        reference_section = "\nReference Examples of Common Issues:\n"
        for idx, example in enumerate(retrieved_examples):
            reference_section += f"\nExample {idx + 1}:\n"
            reference_section += f"Code Snippet:\n{example.get('code_snippet', '')}\n"
            reference_section += f"Explanation: {example.get('explanation', '')}\n"
            reference_section += "-" * 40 + "\n"
```
> Same pattern as `review_prompt.py`, but the header says "Common Issues" instead of "Bad Practices" — slightly different framing that suits translation context better.

```python
    context_section = ""
    if project_context:
        file_list = ", ".join(project_context)
        context_section = f"""
Project Context:
This file exists alongside these other files in the same project directory: {file_list}.
Consider whether naming conventions, import patterns, or architectural styles from sibling files should be preserved in the translation, if relevant.
"""
```
> The project context instruction is translation-specific: it asks Gemini to consider naming conventions and architectural styles from sibling files, which helps produce translations that feel consistent with the rest of the codebase.

```python
    prompt = f"""
You are an expert polyglot programmer.
Translate the following code from {source_language} to {target_language}.

Instructions:
1. Preserve the original logic, structure, and behavior of the code. Do not just produce syntactically valid code; ensure that it computes the exact same results.
2. Return ONLY the translated code.
3. Do not include any explanations, markdown code blocks (e.g. ```), metadata, comments, or introductory/concluding commentary. The output must be ready to write directly to a file.
4. Return the code as a single block of raw code.
{reference_section}{context_section}
Source Code ({source_language}):
{code}
"""
    return prompt.strip()
```
> The critical constraint here is instruction 2-4: "Return ONLY the translated code" and "Do not include markdown code blocks". Without these explicit instructions, LLMs consistently wrap output in ` ``` ` code fences with explanatory text. Those instructions ensure the output can be written directly to a file without post-processing. Instruction 1 emphasises behavioral equivalence, not just syntactic conversion.

---

## 10. `ai_agent/prompts/explanation_prompt.py`

**Purpose:** Builds the exact text prompt for code explanation, framed as a senior developer onboarding a new team member.

---

```python
# Sanjeevni domain - Explanation prompts
```
> Module ownership comment.

```python
def build_explanation_prompt(code: str, language: str = "python", retrieved_examples: list[dict] = None, project_context: list[str] = None) -> str:
    """
    Returns a prompt instructing Gemini to explain, in plain language,
    what the given code does.
    """
```
> The function signature is identical in shape to `build_review_prompt`, just without `source_language`/`target_language`.

```python
    reference_section = ""
    if retrieved_examples:
        reference_section = "\nReference Examples of Code Context/Explanations:\n"
        for idx, example in enumerate(retrieved_examples):
            reference_section += f"\nExample {idx + 1}:\n"
            reference_section += f"Code Snippet:\n{example.get('code_snippet', '')}\n"
            reference_section += f"Explanation: {example.get('explanation', '')}\n"
            reference_section += "-" * 40 + "\n"
```
> The header is "Code Context/Explanations" — the RAG examples show Gemini what "good explanation" looks like for similar code patterns.

```python
    context_section = ""
    if project_context:
        file_list = ", ".join(project_context)
        context_section = f"""
Project Context:
This file exists alongside these other files in the same project directory: {file_list}.
Consider how this code fits into the surrounding project files, or if it interacts with them, when explaining its role.
"""
```
> The explanation-specific context instruction asks Gemini to explain how the code *fits into the project*, not just what it does in isolation. This produces richer explanations that mention related files.

```python
    prompt = f"""
You are a helpful, senior developer onboarding a new team member.
Explain, in plain language, what the following {language} code does.

Instructions:
1. Aim the explanation at a developer who is completely unfamiliar with this part of the codebase.
2. Avoid unnecessary technical jargon unless the concept genuinely requires it. Explain concepts simply and clearly, helping them understand the high-level purpose and logic.
3. Do NOT look for bugs, security issues, code style violations, or reviews. Focus strictly on explaining what the code is doing and how it works.
{reference_section}{context_section}
Code ({language}):
{code}
"""
    return prompt.strip()
```
> The persona ("senior developer onboarding a new team member") sets the tone for a friendly, accessible explanation. Instruction 3 is critical: without it, Gemini tends to mix reviews and bug reports into explanations. The explicit "Do NOT look for bugs" instruction keeps the output focused purely on explanation.

---

## 11. `ai_agent/prompts/multi_agent_prompts.py`

**Purpose:** Builds the two separate prompts used in the multi-agent workflow — one for Agent 1 (Gemini Reviewer) and one for Agent 2 (Groq Verifier).

---

```python
def build_reviewer_prompt(code: str, language: str = "python") -> str:
    """
    Builds the reviewer prompt for Agent 1.
    Instructs Gemini to review the code and output a list of short 1-2 sentence issues.
    """
```
> Unlike the regular review prompt, this one does NOT include RAG examples or project context — the multi-agent workflow is a separate, simpler pipeline focused on the two-agent verification dynamic.

```python
    prompt = f"""
You are a careful, experienced code reviewer.
Review the following {language} code and identify any issues.

For each issue you find, provide a short description.
Keep each issue brief—exactly 1 to 2 sentences. Do not write full prose paragraphs or deep explanations.

Structure your response as a simple list of issues:
Issues:
- <issue 1: short 1-2 sentence description>
- <issue 2: short 1-2 sentence description>

Code:
{code}
"""
    return prompt.strip()
```
> The key constraint "exactly 1 to 2 sentences" keeps the reviewer's output compact, which is important because the entire reviewer output gets passed into the verifier prompt — long verbose output would make the verifier's context window unwieldy.

---

```python
def build_verifier_prompt(code: str, language: str, issues: str) -> str:
    """
    Builds the verifier prompt for Agent 2.
    Instructs Groq to check the issues against the code and only return confirmed issues,
    prefixed with '[VERIFIED BY A SECOND MODEL]'.
    """
```
> Takes THREE arguments: the original code, the language, AND the reviewer's issue list. The verifier needs to see the code itself — not just the issue descriptions — to independently validate whether each issue is real.

```python
    prompt = f"""
You are a critical, independent code verifier.
Analyze the following {language} code and check the list of potential issues identified by another reviewer.

Determine if each issue is a real, valid problem in the code, or if it is a false positive / non-issue.
Only return issues that you confirm are real, valid problems. Drop any issues you disagree with or believe are false positives.

For each confirmed issue, you must prefix it clearly with "[VERIFIED BY A SECOND MODEL]". Keep the explanation brief (1-2 sentences).

Format your response as a simple list of verified issues:
1. [VERIFIED BY A SECOND MODEL] <verified issue and brief explanation>
2. [VERIFIED BY A SECOND MODEL] <verified issue and brief explanation>

Original Code:
{code}

Potential Issues List:
{issues}
"""
    return prompt.strip()
```
> The `[VERIFIED BY A SECOND MODEL]` prefix is a deliberate tagging instruction. It means the final output always carries an explicit label showing which model confirmed each issue — making the multi-agent nature of the result transparent to the end user. The `Potential Issues List:` section at the bottom contains Gemini's raw bullet list, which Groq evaluates point by point.

---

## 12. `cli/commands/review.py`

**Purpose:** The CLI entry-point for the `review` command — validates the file path, reads the file, detects language, calls the review service, prints the result, and writes the walkthrough.

---

```python
import os
import typer
from ai_agent.review_service import review_code
from cli.utils import detect_language
```
> `os` for file existence checks. `typer` is the CLI framework that handles argument parsing and output. `review_code` is the service function that does the actual AI work. `detect_language` is the utility that infers the programming language from the file extension.

```python
def review(
    path: str = typer.Argument(..., help="Path to the file to review")
):
    """
    Review a code file using the Gemini AI agent.
    """
```
> The function decorated by Typer as a CLI command. `typer.Argument(...)` — the `...` (Ellipsis) means this argument is *required*. If the user doesn't provide it, Typer shows a usage error automatically.

```python
    if not os.path.exists(path):
        typer.echo(f"Error: File '{path}' does not exist.", err=True)
        raise typer.Exit(code=1)
```
> First guard: checks the path exists at all. `err=True` routes the error message to `stderr` instead of `stdout` — good CLI practice because it means error messages can be separated from normal output in shell pipelines. `typer.Exit(code=1)` terminates the program with exit code 1, signalling failure to the calling shell.

```python
    if os.path.isdir(path):
        typer.echo(f"Error: '{path}' is a directory. Please provide a file path.", err=True)
        raise typer.Exit(code=1)
```
> Second guard: the path exists but is a directory, not a file. Without this check, the `open()` call below would raise a confusing `IsADirectoryError`.

```python
    try:
        with open(path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        typer.echo(f"Error reading file: {e}", err=True)
        raise typer.Exit(code=1)
```
> Reads the entire file into a string. The context manager ensures the file handle is closed. `encoding="utf-8"` handles files with non-ASCII characters. Any OS-level error (permission denied, corrupted file, etc.) is caught and shown to the user.

```python
    language = detect_language(path)
```
> Determines the programming language by inspecting the file extension. The returned string (e.g. `"python"`) is passed into the review service and the prompt.

```python
    try:
        typer.echo(f"Reviewing {path} (detected language: {language})...\n")
        review_result = review_code(code_content, language, file_path=path)
        typer.echo(review_result)
    except Exception as e:
        typer.echo(f"Error during code review: {e}", err=True)
        raise typer.Exit(code=1)
```
> Prints a status line, calls the review service (which internally handles MCP, RAG, and the Gemini call), prints the full review result to stdout, and catches any fatal errors.

```python
    try:
        from ai_agent.walkthrough_writer import write_review_walkthrough
        write_review_walkthrough(path, language, review_result)
    except Exception as e:
        typer.echo(f"\n[Warning] Could not generate walkthrough file: {e}", err=True)
```
> Writes the walkthrough file in a *separate* try-except from the review itself. This means a walkthrough write failure never causes the CLI command to exit with an error code — the user already saw their review result, and the walkthrough is a bonus output. The `\n` before `[Warning]` adds visual separation.

---

## 13. `cli/commands/translate.py`

**Purpose:** The CLI entry-point for the `translate` command — identical structure to `review.py` but adds a `--to` option for specifying the target language.

---

```python
import os
import typer
from ai_agent.translation_service import translate_code
from cli.utils import detect_language
```
> Same four imports as `review.py`, but importing `translate_code` instead of `review_code`.

```python
def translate(
    path: str = typer.Argument(..., help="Path to the file to translate"),
    to: str = typer.Option(..., "--to", help="Target language for translation")
):
```
> Two parameters: `path` (a positional `Argument`, required) and `to` (a named `Option`, also required because of `...`). `typer.Option` means the user provides it as `--to java` rather than positionally. Without `--to`, Typer shows a usage error.

```python
    if not os.path.exists(path):
        typer.echo(f"Error: File '{path}' does not exist.", err=True)
        raise typer.Exit(code=1)

    if os.path.isdir(path):
        typer.echo(f"Error: '{path}' is a directory. Please provide a file path.", err=True)
        raise typer.Exit(code=1)
```
> Same two file validation guards as in `review.py`.

```python
    try:
        with open(path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        typer.echo(f"Error reading file: {e}", err=True)
        raise typer.Exit(code=1)

    source_language = detect_language(path)
```
> Reads the file and detects the source language. Note the variable is named `source_language` here (vs just `language` in `review.py`) to be explicit about what it represents.

```python
    try:
        typer.echo(f"Translating {path} (from {source_language} to {to})...\n")
        translation_result = translate_code(code_content, source_language, to, file_path=path)
        typer.echo(translation_result)
    except Exception as e:
        typer.echo(f"Error during code translation: {e}", err=True)
        raise typer.Exit(code=1)
```
> The status message includes both language names. `translate_code` receives the `to` variable directly — no normalisation needed here; the service and prompt handle any capitalisation differences.

```python
    try:
        from ai_agent.walkthrough_writer import write_translation_walkthrough
        write_translation_walkthrough(path, source_language, to, translation_result)
    except Exception as e:
        typer.echo(f"\n[Warning] Could not generate walkthrough file: {e}", err=True)
```
> Same non-fatal walkthrough write pattern. Passes all four required arguments: the file path, source language, target language, and the translated code itself.

---

## 14. `cli/commands/explain.py`

**Purpose:** The CLI entry-point for the `explain` command — same structure as `review.py` but calls `explain_code` and uses `write_explanation_walkthrough`.

---

```python
import os
import typer
from ai_agent.explanation_service import explain_code
from ai_agent.walkthrough_writer import write_explanation_walkthrough
from cli.utils import detect_language
```
> Five imports — one more than `review.py`. Unlike the other two CLI commands which import the walkthrough writer inside the `try` block at the bottom, `explain.py` imports `write_explanation_walkthrough` at the top level. This is safe because that function catches all its own exceptions and never raises.

```python
def explain(
    path: str = typer.Argument(..., help="Path to the file to explain")
):
    """
    Explain what a code file does in plain language using the Gemini AI agent.
    """
```
> Only one required argument — no `--to` flag, since explanation doesn't need a target language.

```python
    if not os.path.exists(path):
        typer.echo(f"Error: File '{path}' does not exist.", err=True)
        raise typer.Exit(code=1)

    if os.path.isdir(path):
        typer.echo(f"Error: '{path}' is a directory. Please provide a file path.", err=True)
        raise typer.Exit(code=1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        typer.echo(f"Error reading file: {e}", err=True)
        raise typer.Exit(code=1)

    language = detect_language(path)
```
> Identical validation, file reading, and language detection to the other two CLI commands.

```python
    try:
        typer.echo(f"Explaining {path} (detected language: {language})...\n")
        explanation_result = explain_code(code_content, language, file_path=path)
        typer.echo(explanation_result)
        saved_path = write_explanation_walkthrough(path, language, explanation_result)
        if saved_path:
            typer.echo(f"\nExplanation walkthrough saved to: {saved_path}")
    except Exception as e:
        typer.echo(f"Error during code explanation: {e}", err=True)
        raise typer.Exit(code=1)
```
> The key difference from `review.py` and `translate.py`: `write_explanation_walkthrough` is called *inside* the main `try` block alongside `explain_code`, not in a separate `try` below. This is safe because `write_explanation_walkthrough` never raises — it catches all its own errors internally and returns `""` on failure. The `if saved_path:` check means the "saved to:" line only prints if the file was actually written successfully.

---

## 15. `cli/utils.py`

**Purpose:** A tiny shared utility module containing the language detection function used by all three CLI commands.

---

```python
import os
```
> Only `os` is needed — for `os.path.splitext`.

```python
def detect_language(path: str) -> str:
    """
    Detects the programming language of a file based on its extension.
    Defaults to 'python' if the extension is unrecognized.
    """
```
> A pure function (no side effects) that takes a file path string and returns a language name string.

```python
    _, ext = os.path.splitext(path)
```
> `os.path.splitext` splits a path into `(base, extension)`. The `_` discards the base name — we only care about the extension. For `"test_sample.py"` this returns `("test_sample", ".py")`.

```python
    ext = ext.lower()
```
> Normalises the extension to lowercase so `.PY`, `.Py`, and `.py` all match the same key in the dictionary below.

```python
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".java": "java",
    }
    return extension_map.get(ext, "python")
```
> A lookup table mapping extensions to language names. `.get(ext, "python")` returns the matched language, or `"python"` as the default if the extension isn't in the map. The default-to-Python choice reflects that the system was originally built for Python code.

---

## 16. `mcp_server/server.py`

**Purpose:** Implements the Model Context Protocol (MCP) server that exposes file listing tools to AI agents; runs as a subprocess communicating over `stdio`.

---

```python
import asyncio
```
> Imports Python's built-in `asyncio` library. The MCP server is asynchronous — it awaits incoming tool calls rather than blocking on each one. `asyncio.run()` is used at the bottom to start the event loop.

```python
import sys
```
> Used at the bottom to write the startup message to `stderr` (`file=sys.stderr`) rather than `stdout`, so the message doesn't interfere with the stdio protocol stream.

```python
from mcp.server.stdio import stdio_server
```
> Imports the `stdio_server` async context manager from the official MCP SDK. MCP communicates via JSON-RPC messages over standard input/output — `stdio_server` handles the low-level framing of those messages.

```python
from mcp.server import Server
```
> Imports the `Server` class that manages the MCP server lifecycle and routes incoming requests to the appropriate handler functions.

```python
from mcp.types import Tool, TextContent
```
> Imports two schema types. `Tool` is the data class used to describe each available tool (name, description, input schema). `TextContent` is the wrapper for text responses returned by tool calls.

```python
from mcp_server.tools import list_local_files, list_github_repo_files
```
> Imports the two tool implementations from the sibling `tools.py` file. The server only handles routing — the actual logic lives in `tools.py`.

```python
app = Server("kritiq-mcp-server")
```
> Creates the MCP server instance with the name `"kritiq-mcp-server"`. This name is used during the MCP handshake to identify the server.

---

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
```
> Registers this async function as the handler for MCP's `tools/list` request — when an AI agent asks "what tools are available?", this function runs and returns the list.

```python
    return [
        Tool(
            name="list_local_files",
            description="List files and directories inside a local filesystem directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The local directory path to list. Defaults to the current directory ('.').",
                        "default": "."
                    }
                }
            }
        ),
```
> Describes the first tool using JSON Schema. The `inputSchema` tells MCP-aware clients what arguments this tool accepts. The `directory` property is a string with a default value of `"."`. No `"required"` field means all properties are optional.

```python
        Tool(
            name="list_github_repo_files",
            description="List files and directories at a given path inside a public GitHub repository, using the GitHub REST API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "The GitHub username or organisation that owns the repository (e.g. 'octocat')."
                    },
                    "repo": {
                        "type": "string",
                        "description": "The name of the repository (e.g. 'Hello-World')."
                    },
                    "path": {
                        "type": "string",
                        "description": "The path inside the repository to list. Defaults to the root ('').",
                        "default": ""
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
    ]
```
> The second tool's schema. `"required": ["owner", "repo"]` tells clients that `owner` and `repo` must be provided, but `path` is optional (defaults to `""`  — the repo root).

---

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution requests."""
```
> Registers this as the handler for MCP's `tools/call` request — when an AI agent says "run this tool with these arguments", this function dispatches to the right implementation.

```python
    if name == "list_local_files":
        directory = arguments.get("directory", ".")
        files = list_local_files(directory)
        return [TextContent(type="text", text="\n".join(files))]
```
> If the tool name matches, extracts the `directory` argument (defaulting to `"."`), calls the implementation, joins the file list into a newline-separated string, and wraps it in a `TextContent` object (the type MCP requires for text responses).

```python
    if name == "list_github_repo_files":
        owner = arguments["owner"]
        repo = arguments["repo"]
        path = arguments.get("path", "")
        files = list_github_repo_files(owner, repo, path)
        return [TextContent(type="text", text="\n".join(files))]
```
> Same pattern for the GitHub tool. `arguments["owner"]` uses direct key access (not `.get()`) because `owner` is required — if it's missing, we want a `KeyError` rather than a silent empty call.

```python
    raise ValueError(f"Unknown tool: {name}")
```
> If neither condition matched, the requested tool name doesn't exist. Raising here follows the MCP protocol convention for unknown tool requests.

---

```python
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
```
> The async main function. `stdio_server()` is an async context manager that sets up the stdin/stdout streams for MCP communication. `app.run()` starts the server event loop, reading JSON-RPC requests from `read_stream` and writing responses to `write_stream`.

```python
if __name__ == "__main__":
    print("Starting MCP server...", file=sys.stderr)
    asyncio.run(main())
```
> When run directly, prints a startup message to `stderr` (not `stdout`, which is reserved for MCP protocol messages), then starts the asyncio event loop with `main()`.

---

## 17. `mcp_server/tools.py`

**Purpose:** Contains the actual implementations of the two MCP tools — local file listing and GitHub repo file listing — keeping implementation logic separate from the server routing code.

---

```python
import os
from repo_integration.github_api import list_repo_files
```
> `os` for local file system operations. `list_repo_files` is imported from `github_api.py` to handle GitHub calls — `tools.py` acts as a thin adapter, not duplicating the GitHub logic.

```python
def list_local_files(directory: str = ".") -> list[str]:
    """
    Returns a list of filenames in the given local directory.
    """
    try:
        if not os.path.exists(directory):
            return [f"Error: Directory '{directory}' does not exist."]
        if not os.path.isdir(directory):
            return [f"Error: '{directory}' is not a directory."]
        return os.listdir(directory)
    except Exception as e:
        return [f"Error: {e}"]
```
> Returns error messages *inside* the list rather than raising exceptions. This is the intentional contract of this function — callers (like `review_service.py`) use `any(f.startswith("Error:") for f in result)` to detect failures. `os.listdir(directory)` returns all file and directory names in the given path, unsorted. The inner `try-except` catches any unexpected OS error.

```python
def list_github_repo_files(owner: str, repo: str, path: str = "") -> list[str]:
    """
    Returns a list of file/directory names at the given path inside a
    public GitHub repository, using the GitHub REST API.
    """
    return list_repo_files(owner, repo, path)
```
> A pure pass-through function. Its purpose is to give `server.py` a single import target (`from mcp_server.tools import ...`) and to keep all GitHub-specific logic in `repo_integration/github_api.py`.

---

## 18. `rag_pipeline/embeddings.py`

**Purpose:** Generates high-dimensional text embedding vectors using the Gemini embedding model; these vectors are the mathematical foundation of the RAG semantic search system.

---

```python
import time
from google.genai.errors import ClientError
from ai_agent.gemini_client import client
```
> `time` for duration measurement. `ClientError` is the specific Gemini SDK exception class for embedding API errors. `client` is imported directly from `gemini_client.py` — this is the already-configured `genai.Client` instance, reused here to avoid creating a second connection.

```python
def get_embedding(text: str) -> list[float]:
    """
    Generates a high-dimensional text embedding vector using the gemini-embedding-2 model.
    """
    start_time = time.perf_counter()
```
> Defines the function. Takes any text string and returns a list of floating-point numbers — the embedding vector. Starts the timer.

```python
    try:
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=text
        )
```
> Calls Gemini's embedding model (`gemini-embedding-2`). Unlike `generate_content` (which takes a user role and generates text), `embed_content` converts text into a vector without generating any new content — it's a one-way mathematical transformation.

```python
        values = response.embeddings[0].values
        return values
```
> Extracts the vector from the response. `embeddings[0]` gets the first (and only) embedding result. `.values` is the list of float numbers. The vector typically has 3072 dimensions for `gemini-embedding-2`.

```python
    except ClientError as e:
        print(f"Gemini Embedding API error: {e}")
        raise RuntimeError(f"Gemini Embedding API error: {e}") from e
    except Exception as e:
        print(f"Unexpected error generating embedding: {e}")
        raise RuntimeError(f"An unexpected error occurred during embedding: {e}") from e
```
> Two exception handlers: one for Gemini-specific embedding errors, one for anything else. Both print and re-raise as `RuntimeError` so the calling code in `retriever.py` can handle them cleanly.

```python
    finally:
        duration = time.perf_counter() - start_time
        print(f"Embedding call took {duration:.2f} seconds")
```
> Always prints the embedding call duration — important feedback since embedding calls add up when processing 72 dataset entries.

```python
if __name__ == "__main__":
    try:
        vector = get_embedding("Testing the RAG embedding generation pipeline.")
        print(f"Success! Vector length: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
    except Exception as e:
        print(f"Test failed: {e}")
```
> Quick smoke-test: embeds a test sentence, prints the vector length (confirming the model returns the expected dimensionality) and the first 5 values (confirming the numbers are reasonable floats, not all zeros).

---

## 19. `rag_pipeline/retriever.py`

**Purpose:** Implements the complete RAG pipeline — loading datasets, generating and caching embeddings, computing cosine similarity, and retrieving the most relevant examples for a given query.

---

```python
import json
import math
import os
from rag_pipeline.embeddings import get_embedding
```
> `json` for reading/writing dataset and cache files. `math` for `math.sqrt` used in the cosine similarity calculation. `os` for file existence checks and directory listing. `get_embedding` from the sibling module for generating vectors.

---

```python
def load_dataset_with_embeddings(filepath: str) -> list[dict]:
```
> Loads a single dataset JSON file and generates an embedding for every entry in it. Returns the same list of dicts with an `"embedding"` key added to each.

```python
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")
```
> Validates the file exists before trying to open it — gives a clear error message instead of a generic `FileNotFoundError` from `open()`.

```python
    with open(filepath, "r", encoding="utf-8") as f:
        dataset = json.load(f)
```
> Reads and parses the entire JSON file into a Python list of dicts. `encoding="utf-8"` is needed because the dataset files contain Unicode characters (quotes, dashes, emoji in some explanations).

```python
    if not isinstance(dataset, list):
        raise ValueError("Dataset root must be a JSON array (list).")
```
> Validates the JSON structure. Our schema requires the top-level element to be a list. A dict at the root would be a corrupted or wrong file.

```python
    print(f"Loaded {len(dataset)} entries from {filepath}. Generating embeddings...")
```
> Progress message — useful because generating embeddings for 8 entries takes several seconds.

```python
    for index, entry in enumerate(dataset):
        entry_id = entry.get("id", f"index_{index}")
        print(f"Generating embedding for {entry_id}...")
        combined_text = f"code_snippet: {entry.get('code_snippet', '')}\nexplanation: {entry.get('explanation', '')}"
        entry["embedding"] = get_embedding(combined_text)
```
> For each entry, creates a combined text by joining the code snippet and explanation with a label prefix. This combined representation is more semantically rich than either field alone — the embedding captures both what the code looks like AND what it means. The resulting vector is stored back in the dict under the key `"embedding"`.

```python
    print("All dataset embeddings generated successfully.")
    return dataset
```
> Final status message and returns the modified dataset list.

---

```python
def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
```
> Implements cosine similarity from scratch using Python's `math` module — no NumPy dependency required.

```python
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be of equal length.")
```
> Validates vector dimensions match. Two vectors of different lengths can't be compared meaningfully.

```python
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
```
> The dot product: multiply each pair of corresponding numbers and sum all the results. `zip` pairs elements by position.

```python
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
```
> The magnitude (length) of each vector: sum the squares of all elements, then take the square root. This is the Euclidean norm.

```python
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
```
> Guards against division by zero. A zero-magnitude vector (all elements are 0) has no direction, so similarity is undefined — we return 0.0 as the neutral value.

```python
    return dot_product / (magnitude_a * magnitude_b)
```
> The cosine similarity formula: `dot(A, B) / (|A| * |B|)`. Returns a value between -1.0 and 1.0. For text embeddings, values are typically in the range 0.5–0.99, with higher values meaning more semantically similar text.

---

```python
def retrieve_similar_examples(query_text: str, dataset_with_embeddings: list[dict], top_k: int = 3) -> list[dict]:
```
> The main retrieval function. Takes a query string, the in-memory dataset (already embedded), and a count of how many top results to return.

```python
    print(f"Generating embedding for query text...")
    query_embedding = get_embedding(query_text)
```
> Embeds the query text. This is the one embedding API call per retrieval — the dataset embeddings are already cached.

```python
    scored_entries = []
    for entry in dataset_with_embeddings:
        if "embedding" not in entry:
            continue
        similarity = cosine_similarity(query_embedding, entry["embedding"])
```
> Iterates over every dataset entry and computes its similarity score against the query. Entries without an `"embedding"` key are skipped (defensive check).

```python
        entry_copy = entry.copy()
        if "embedding" in entry_copy:
            del entry_copy["embedding"]
        entry_copy["similarity_score"] = similarity
        scored_entries.append(entry_copy)
```
> Makes a *copy* of the entry dict before modifying it — important because we don't want to delete the `"embedding"` key from the actual dataset in memory. Removes the embedding vector from the copy (it's a list of 3072 floats — including it in the prompt would waste tokens), then adds the similarity score.

```python
    scored_entries.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_entries[:top_k]
```
> Sorts all entries from highest to lowest similarity score, then returns only the top `k` results.

---

```python
def get_or_build_cached_embeddings(filepath: str, cache_path: str = None) -> list[dict]:
```
> A caching layer for a single dataset file's embeddings. Avoids re-calling the embedding API (which costs money and takes time) on every run.

```python
    if cache_path is None:
        base, ext = os.path.splitext(filepath)
        cache_path = f"{base}.embeddings.json"
```
> If no custom cache path is given, auto-generates one by replacing the file extension. `"bad_practice.json"` → `"bad_practice.embeddings.json"`.

```python
    if os.path.exists(cache_path):
        print(f"Loading dataset embeddings from cache file: {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load embeddings cache from {cache_path}: {e}. Re-building...")
```
> If the cache file exists, loads and returns it without touching the Gemini API. If the cache is corrupted (malformed JSON, truncated file, etc.), warns and falls through to re-build.

```python
    print(f"No valid cache found at {cache_path}. Building fresh embeddings...")
    dataset_with_embeddings = load_dataset_with_embeddings(filepath)
```
> Cache miss path: calls the embedding generator for the full dataset.

```python
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(dataset_with_embeddings, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved embeddings to cache file: {cache_path}")
    except Exception as e:
        print(f"Warning: Failed to write embeddings cache to {cache_path}: {e}")
```
> Saves the freshly-generated embeddings to the cache file. `ensure_ascii=False` preserves Unicode characters in the JSON. The save failure is a warning, not a fatal error — the function still returns the data even if caching fails.

---

```python
def load_all_dataset_files(directory: str = "dataset/processed") -> list[str]:
```
> Scans a directory and returns paths to all source dataset JSON files, excluding cache files.

```python
    if not os.path.isdir(directory):
        print(f"Warning: Directory {directory} does not exist.")
        return []
```
> Returns empty list rather than raising if the directory doesn't exist — allows the rest of the system to handle a missing dataset directory gracefully.

```python
    dataset_files = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json") and not filename.endswith(".embeddings.json"):
            dataset_files.append(os.path.join(directory, filename))
    return dataset_files
```
> `sorted()` ensures consistent ordering across runs (important for reproducible combined caches). The double condition `endswith(".json") and not endswith(".embeddings.json")` specifically excludes the per-file cache files from the source list.

---

```python
def get_or_build_combined_embeddings(
    directory: str = "dataset/processed",
    cache_path: str = "dataset/processed/_combined.embeddings.json"
) -> list[dict]:
```
> The top-level function called by all three service files. Discovers all 9 dataset files, loads/builds embeddings for each one (reusing per-file caches), merges them into one list of 72 entries, and caches the combined result.

```python
    if os.path.exists(cache_path):
        print(f"Loading combined dataset embeddings from cache: {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                combined = json.load(f)
            print(f"Loaded {len(combined)} total entries from combined cache.")
            return combined
        except Exception as e:
            print(f"Warning: Failed to load combined cache from {cache_path}: {e}. Rebuilding...")
```
> Fast path: if the combined cache exists (e.g. `_combined.embeddings.json`), loads it in one `json.load()` call and returns immediately. This is what happens on the vast majority of runs.

```python
    source_files = load_all_dataset_files(directory)
    if not source_files:
        print(f"No dataset files found in {directory}.")
        return []
```
> Slow path: discovers all source files. Returns early if none found.

```python
    print(f"Found {len(source_files)} dataset file(s) to combine:")
    for f in source_files:
        print(f"  - {f}")
```
> Prints the list of files about to be processed — useful feedback for the first run or after adding new files.

```python
    combined = []
    for filepath in source_files:
        print(f"\nProcessing: {filepath}")
        file_entries = get_or_build_cached_embeddings(filepath)
        combined.extend(file_entries)
```
> Processes each file: if that file's per-file cache exists, loads it; otherwise, generates and saves its embeddings. `combined.extend(file_entries)` appends all entries from that file into the master list.

```python
    print(f"\nCombined {len(combined)} total entries from {len(source_files)} file(s).")
```
> After the loop, prints the total count — this is where "Combined 72 total entries from 9 file(s)." appears in the terminal.

```python
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        print(f"Saved combined embeddings cache to: {cache_path}")
    except Exception as e:
        print(f"Warning: Failed to write combined cache to {cache_path}: {e}")

    return combined
```
> Saves the full 72-entry combined list to `_combined.embeddings.json`, then returns it. Future calls will load this file directly, skipping all embedding generation.

---

## 20. `repo_integration/github_api.py`

**Purpose:** Wraps the GitHub REST API to list files in repositories, with optional authentication via a personal access token loaded from the environment.

---

```python
import os
import requests
from dotenv import load_dotenv
```
> `os` for reading the environment variable. `requests` is the third-party HTTP client library used to call the GitHub REST API. `load_dotenv` to load the `.env` file.

```python
load_dotenv()
```
> Loads `.env` into the process environment at module import time.

```python
GITHUB_API_BASE = "https://api.github.com"
```
> A module-level constant for the GitHub API base URL. Centralising it here means if GitHub ever changes their domain or API version, there's only one place to update.

```python
_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
```
> Reads the optional GitHub Personal Access Token. The leading underscore `_` is a Python convention for "private to this module" — external code should use the `HEADERS` dict rather than accessing this variable directly. `os.environ.get(...)` returns `None` if not set, which is fine — it's optional.

```python
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
```
> The base headers sent with every request. `Accept: application/vnd.github+json` tells GitHub to respond with its preferred JSON format. `X-GitHub-Api-Version: 2022-11-28` pins to a specific API version, ensuring the response format doesn't change if GitHub updates their API.

```python
if _GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {_GITHUB_TOKEN}"
    print("GitHub API: authenticated (5,000 req/hour, private repo access enabled)")
else:
    print("GitHub API: using unauthenticated requests (60/hour limit)")
```
> At module load time, conditionally adds the Authorization header. If a token is present, uses "Bearer" token authentication (the modern GitHub auth scheme). The print messages are a one-time notification — they appear once when the module is first imported, not on every API call.

---

```python
def list_repo_files(owner: str, repo: str, path: str = "") -> list[str]:
    """
    Calls the GitHub REST API to list files and directories at the given
    path inside a repository. Returns a list of entry names.

    Uses an authenticated request if GITHUB_TOKEN is set in the environment,
    falling back to unauthenticated (60 req/hour) otherwise.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
```
> Constructs the GitHub Contents API URL. For `owner="octocat"`, `repo="Hello-World"`, `path=""`, this becomes `"https://api.github.com/repos/octocat/Hello-World/contents/"` — the repository root.

```python
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.ConnectionError:
        return ["Error: could not connect to GitHub API — check your network connection."]
    except requests.exceptions.Timeout:
        return ["Error: request to GitHub API timed out."]
```
> Makes the HTTP GET request. `timeout=10` limits it to 10 seconds. Two specific exceptions are caught and returned as error strings (same "errors in the list" contract as `list_local_files`).

```python
    if response.status_code == 404:
        return ["Error: repository or path not found."]
```
> GitHub returns 404 both for non-existent repos and non-existent paths within a repo.

```python
    if response.status_code == 403:
        if int(response.headers.get("X-RateLimit-Remaining", -1)) == 0:
            reset_ts = response.headers.get("X-RateLimit-Reset", "unknown")
            return [f"Error: GitHub API rate limit exceeded. Quota resets at Unix timestamp {reset_ts}."]
        return ["Error: access forbidden — the repository may be private or the request was blocked."]
```
> GitHub returns 403 for two distinct cases: rate limit exceeded (the `X-RateLimit-Remaining` header will be `0`) and genuinely forbidden access (private repo without auth, or IP blocked). We differentiate them to give the user actionable information — "wait for rate limit reset" vs "you need authentication".

```python
    if response.status_code != 200:
        return [f"Error: unexpected GitHub API response {response.status_code}."]
```
> Catch-all for any other non-200 status code (e.g. 500 GitHub server error, 301 redirect not followed).

```python
    data = response.json()

    if isinstance(data, dict):
        return [data.get("name", "")]

    return [entry["name"] for entry in data]
```
> The GitHub Contents API returns a JSON *list* when the path is a directory (each element is a file/directory entry) and a JSON *dict* when the path points to a single file. We handle both cases: for a dict, wrap the single filename in a list; for a list, extract just the `name` field from each entry.

---

## 21. `dataset/schema.py`

**Purpose:** Defines the `DatasetEntry` TypedDict — the shared type contract that all 9 dataset JSON files must conform to, with support for optional extra fields used by translation pairs.

---

```python
# Sanjeevni domain - Dataset item representation schema
from typing import TypedDict, List
```
> `TypedDict` is a special class from Python's `typing` module that lets you define dictionary types with specific key names and value types. `List` is used for the `tags` field type hint.

```python
class _DatasetEntryRequired(TypedDict):
    """Required fields present in every dataset entry."""
    id: str
    category: str
    language: str
    code_snippet: str
    explanation: str
    tags: List[str]
```
> Defines the base class with all 6 required fields. The leading underscore `_` marks this as an internal implementation detail — external code should use `DatasetEntry`, not this base. By separating required from optional fields into two classes, we use TypedDict's inheritance feature to correctly describe an "extension" of the base schema.

```python
class DatasetEntry(_DatasetEntryRequired, total=False):
    """Full dataset entry schema.

    Extends the required base fields with optional fields used by
    specific categories (e.g. translation_pairs).

    Optional fields
    ---------------
    translated_language : str
        The target language name for a translation-pair entry
        (e.g. 'java', 'javascript').
    translated_snippet : str
        The equivalent code snippet in ``translated_language``.
    """

    translated_language: str
    translated_snippet: str
```
> Inherits all 6 required fields from `_DatasetEntryRequired`. `total=False` means the fields declared in *this* class (`translated_language`, `translated_snippet`) are optional — they don't need to be present. Fields inherited from the parent remain required. This two-class TypedDict pattern is the standard Python way to mix required and optional keys in a typed dictionary.

---

## 22. `dataset/build_dataset.py`

**Purpose:** Contains the `validate_dataset_file()` function used to verify that any JSON dataset file matches the `DatasetEntry` schema, and placeholder functions for future dataset loading and embedding pipeline work.

---

```python
# Sanjeevni domain - Dataset build pipeline (loading raw and processing into MongoDB Atlas)
import json
import os
```
> Module comment documenting the intended future scope (MongoDB Atlas pipeline). `json` for loading dataset files. `os` for checking file existence.

```python
def load_and_clean_examples():
    # TODO: Load raw files, clean and validate them
    pass

def generate_embeddings_and_push():
    # TODO: Generate vectors and upload to MongoDB
    pass
```
> Two stub functions with TODO comments. They are intentional placeholders — the full pipeline (loading raw examples, cleaning them, generating embeddings, and pushing to MongoDB Atlas) is planned but not yet implemented. `pass` is the minimum valid function body in Python.

---

```python
def validate_dataset_file(filepath: str) -> bool:
    """
    Loads the JSON file and checks if every entry matches the DatasetEntry shape.
    Prints which entries fail validation (if any), and returns True if all are valid.
    """
```
> The working function. Returns a boolean: `True` if every entry in the file passes validation, `False` if any fail.

```python
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist.")
        return False
```
> First check: the file must exist. Returns `False` immediately rather than crashing with a `FileNotFoundError`.

```python
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load JSON from {filepath}. Exception: {e}")
        return False
```
> Tries to parse the file as JSON. `json.load()` raises for malformed JSON (syntax errors, BOM characters, etc.). We catch any exception, print the error, and return `False`.

```python
    if not isinstance(data, list):
        print(f"Error: The root of the dataset in {filepath} must be a JSON array (list).")
        return False
```
> Validates the top-level structure is a JSON array. A JSON object at the root (e.g. `{}`) is invalid for our schema.

```python
    required_keys = {
        "id": str,
        "category": str,
        "language": str,
        "code_snippet": str,
        "explanation": str,
        "tags": list,
    }
```
> Defines which keys every entry must have and what Python type each value must be. `list` (not `List[str]`) because `isinstance(value, list)` works at runtime while generic types like `List[str]` don't. This dictionary drives the validation loop below.

```python
    all_valid = True
```
> A flag that starts `True` and gets flipped to `False` the moment any validation failure is found. The loop continues even after a failure (so all errors are reported, not just the first one).

```python
    for index, entry in enumerate(data):
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        label = f"entry at index {index} (id: {entry_id})" if entry_id else f"entry at index {index}"
```
> Creates a human-readable label for each entry used in error messages. `enumerate` gives both the position and the value. If the entry isn't a dict yet, `entry.get("id")` would crash, so `isinstance(entry, dict)` is checked first.

```python
        if not isinstance(entry, dict):
            print(f"Validation failure: {label} is not a JSON object (dictionary).")
            all_valid = False
            continue
```
> If an entry isn't a dict (e.g. it's a string or number), prints a failure message, marks the flag, and uses `continue` to skip the key-checking loop for this entry.

```python
        missing_or_invalid = []

        for key, expected_type in required_keys.items():
            if key not in entry:
                missing_or_invalid.append(f"missing '{key}'")
                continue

            val = entry[key]
            if not isinstance(val, expected_type):
                missing_or_invalid.append(f"'{key}' is of type {type(val).__name__}, expected {expected_type.__name__}")
                continue
```
> For each required key, checks whether it's present and whether its value is the right type. `type(val).__name__` and `expected_type.__name__` give human-readable type names like `"int"` or `"str"` in the error message.

```python
            if key == "tags":
                for tag_index, tag in enumerate(val):
                    if not isinstance(tag, str):
                        missing_or_invalid.append(f"tag at index {tag_index} is of type {type(tag).__name__}, expected str")
```
> Extra validation for the `tags` field: checks that every element *within* the list is a string. A `tags` value of `[1, 2, 3]` would pass the `isinstance(val, list)` check above but fail here.

```python
        if missing_or_invalid:
            print(f"Validation failure for {label}: {', '.join(missing_or_invalid)}")
            all_valid = False
```
> If any issues were collected, prints them all in one line (comma-separated) and marks the flag.

```python
    if all_valid:
        print(f"Success: Dataset file {filepath} is valid!")
    else:
        print(f"Failure: One or more entries in {filepath} failed validation.")

    return all_valid
```
> Final summary: prints one of two messages and returns the boolean result.

```python
if __name__ == "__main__":
    import sys
    test_path = "dataset/processed/bad_practice.json"
    print(f"Validating {test_path}...")
    success = validate_dataset_file(test_path)
    sys.exit(0 if success else 1)
```
> When run directly, validates `bad_practice.json` and exits with code 0 (success) or 1 (failure) — making it usable in shell scripts and CI pipelines where exit codes matter.

---

## End of Walkthrough

*This document was generated by reading the source code directly. No API calls were made during its creation. Total files covered: 22. Total lines of code annotated: ~780.*

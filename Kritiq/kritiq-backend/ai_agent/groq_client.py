import os
import time
from dotenv import load_dotenv
from groq import Groq
from groq import GroqError

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

# Configure the client
client = Groq(
    api_key=API_KEY,
    timeout=30.0  # 30 seconds request timeout
)


def ask_groq(prompt: str) -> str:
    """
    Calls Groq API with the provided prompt using llama-3.3-70b-versatile.
    """
    start_time = time.perf_counter()
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
        # Extract response text
        content = chat_completion.choices[0].message.content
        if content is None:
            return ""
        return content
    except GroqError as e:
        print(f"Groq API error: {e}")
        raise RuntimeError(f"Groq API error occurred: {e}") from e
    except Exception as e:
        print(f"Unexpected error in Groq call: {e}")
        raise RuntimeError(f"An unexpected error occurred while calling Groq: {e}") from e
    finally:
        duration = time.perf_counter() - start_time
        print(f"Groq call took {duration:.2f} seconds")


if __name__ == "__main__":
    # Small test block
    try:
        res = ask_groq("Hello! Write a 1-sentence test message.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Error: {e}")

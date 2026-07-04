# Sanjeevni domain - Google Gemini API client setup
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        # TODO: Initialize Gemini SDK
        # genai.configure(api_key=api_key)
        pass

    async def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        # TODO: Call gemini model
        return "Mock response from Gemini API"

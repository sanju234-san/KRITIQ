# Sanjeevni domain - Review prompts

REVIEW_SYSTEM_INSTRUCTION = """
You are an expert software engineer and a thorough code reviewer.
Analyze the target code and provide a structured JSON response identifying potential issues, severities, and locations.
"""

REVIEW_PROMPT_TEMPLATE = """
Target Code to Review:
```
{code}
```

Repository Context:
{context}

Similar Examples:
{examples}
"""

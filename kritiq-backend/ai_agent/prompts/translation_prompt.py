# Sanjeevni domain - Translation prompts

TRANSLATION_SYSTEM_INSTRUCTION = """
You are an expert polyglot programmer.
Translate the target code from {source_lang} to {target_lang} preserving the original logic, idiomatic expressions, and conventions.
"""

TRANSLATION_PROMPT_TEMPLATE = """
Source Code ({source_lang}):
```
{code}
```
"""

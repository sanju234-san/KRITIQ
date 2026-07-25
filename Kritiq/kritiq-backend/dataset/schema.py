# Sanjeevni domain - Dataset item representation schema
from typing import TypedDict, List

class _DatasetEntryRequired(TypedDict):
    """Required fields present in every dataset entry."""
    id: str
    category: str
    language: str
    code_snippet: str
    explanation: str
    tags: List[str]


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


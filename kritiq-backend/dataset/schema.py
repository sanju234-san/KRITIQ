# Sanjeevni domain - Dataset item representation schema
from typing import TypedDict, List

class DatasetEntry(TypedDict):
    id: str
    category: str
    language: str
    code_snippet: str
    explanation: str
    tags: List[str]


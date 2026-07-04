# Sanjeevni domain - Dataset item representation schema
from pydantic import BaseModel
from typing import List, Optional

class DatasetEntry(BaseModel):
    id: str
    category: str
    language: str
    code_snippet: str
    explanation: str
    tags: List[str]
    embedding_vector: Optional[List[float]] = None

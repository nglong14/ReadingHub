from typing import List, Optional
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class BookResponse(BaseModel):
    isbn13: Optional[str]
    title: Optional[str]
    authors: Optional[str]
    categories: Optional[str]
    description: Optional[str]
    score: Optional[float]

class SearchResponse(BaseModel):
    results: List[BookResponse]
    total: int
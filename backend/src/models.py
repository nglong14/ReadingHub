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
    thumbnail: Optional[str] = None
    average_rating: Optional[float] = None
    num_pages: Optional[int] = None
    published_year: Optional[int] = None
    score: Optional[float]
    # Emotion scores
    anger: Optional[float] = None
    disgust: Optional[float] = None
    fear: Optional[float] = None
    joy: Optional[float] = None
    sadness: Optional[float] = None
    surprise: Optional[float] = None
    neutral: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[BookResponse]
    total: int

class CreateBook(BaseModel):
    isbn13: int
    title: Optional[str]
    authors: Optional[str]
    categories: Optional[str]
    description: str
    thumbnail: Optional[str] = None
    average_rating: Optional[float] = None
    num_pages: Optional[int] = None
    published_year: Optional[int] = None
    created_by: Optional[str] = None
    needs_embedding: bool = True

class CreateBookResponse(BaseModel):
    isbn13: int
    title: Optional[str]
    authors: Optional[str]
    categories: Optional[str]
    description: str
    thumbnail: Optional[str] = None
    average_rating: Optional[float] = None
    num_pages: Optional[int] = None
    published_year: Optional[int] = None
    created_by: Optional[str] = None
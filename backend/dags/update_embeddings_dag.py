import os
import pendulum
from typing import List, Dict
from supabase import create_client, Client
from airflow.sdk import dag, task
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid

load_dotenv("/mnt/d/BookRecommendation/.env")

# Initialize Supabase client
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@dag(
    schedule="@weekly",
    start_date=pendulum.datetime(2025, 1, 21, tz="UTC"),
    catchup=False,
    tags=["embeddings", "books"],
)
def update_embeddings_dag():
    @task()
    def extract() -> List[Dict]:
        """Extract books with needs_embedding=True from Supabase — full metadata."""
        response = (
            supabase.table("books")
            .select(
                "isbn13,tagged_description,title,authors,categories,description,"
                "thumbnail,average_rating,num_pages,published_year,"
                "anger,disgust,fear,joy,sadness,surprise,neutral"
            )
            .eq("needs_embedding", True)
            .execute()
        )
        books = response.data
        print(f"Extracted {len(books)} books needing embeddings")
        return books

    @task()
    def transform(books: List[Dict]) -> List[Dict]:
        """Validate books and generate embeddings using SentenceTransformer."""
        if not books:
            print("No books to process")
            return []

        valid_books = [b for b in books if b.get("tagged_description")]
        if not valid_books:
            return []

        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [b["tagged_description"] for b in valid_books]
        vectors = model.encode(texts, normalize_embeddings=True).tolist()

        # Attach vector to each book dict
        for book, vector in zip(valid_books, vectors):
            book["_vector"] = vector

        print(f"Generated embeddings for {len(valid_books)} books")
        return valid_books

    @task()
    def load(embedded_books: List[Dict]) -> None:
        if not embedded_books:
            print("No embeddings to load")
            return

        qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=book.pop("_vector"),
                payload={
                    "isbn13": str(book.get("isbn13", "")),
                    "title": book.get("title", ""),
                    "authors": book.get("authors", ""),
                    "categories": book.get("categories", ""),
                    "description": book.get("description", ""),
                    "thumbnail": book.get("thumbnail", ""),
                    "average_rating": book.get("average_rating"),
                    "num_pages": book.get("num_pages"),
                    "published_year": book.get("published_year"),
                    "anger": book.get("anger"),
                    "disgust": book.get("disgust"),
                    "fear": book.get("fear"),
                    "joy": book.get("joy"),
                    "sadness": book.get("sadness"),
                    "surprise": book.get("surprise"),
                    "neutral": book.get("neutral"),
                },
            )
            for book in embedded_books
        ]

        qdrant_client.upsert(collection_name="books", points=points)
        print(f"Upserted {len(points)} points to Qdrant")

        # Mark books as processed in Supabase
        isbn_list = [b["isbn13"] for b in embedded_books]
        for isbn in isbn_list:
            supabase.table("books").update({"needs_embedding": False}).eq("isbn13", isbn).execute()
        print(f"Marked {len(isbn_list)} books as processed")

    # Define task dependencies
    books = extract()
    embedded = transform(books)
    load(embedded)

update_embeddings_dag()

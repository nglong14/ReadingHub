import os
import pendulum
from typing import List, Dict
from supabase import create_client, Client
from airflow.sdk import dag, task
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid

load_dotenv("/mnt/d/BookRecommendation/.env")

# Initialize Supabase client
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@dag(
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 21, tz="UTC"),
    catchup=False,
    tags=["embeddings", "books"],
)
def update_embeddings_dag():
    """
    ETL pipeline to generate and store embeddings for new books
    """
    
    @task()
    def extract() -> List[Dict]:
        """Extract books with needs_embedding=True from Supabase"""
        response = supabase.table("books").select("isbn13, tagged_description").eq("needs_embedding", True).execute()
        books = response.data
        print(f"Extracted {len(books)} books needing embeddings")
        return books

    @task()
    def transform(books: List[Dict]) -> List[Dict]:
        """Validate and prepare books for embedding"""
        if not books:
            print("No books to process")
            return []
        
        # Filter out books without tagged_description
        valid_books = [book for book in books if book.get("tagged_description")]
        
        print(f"Prepared {len(valid_books)} books for embedding")
        return valid_books
    
    @task()
    def load(embedded_books: List[Dict]) -> None:
        """Load embeddings to Qdrant and mark books as processed"""
        if not embedded_books:
            print("No embeddings to load")
            return
        
        # Initialize embedding model (needed for QdrantVectorStore)
        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder="/mnt/d/BookRecommendation/models",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Qdrant client
        from langchain_qdrant import QdrantVectorStore
        qdrant_client = QdrantClient(path="/mnt/d/BookRecommendation/backend/qdrant_storage")
        
        # Connect to existing vector store
        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name="books",
            embedding=embedding_model
        )
        
        # Extract tagged descriptions and add to vector store
        texts = [book["tagged_description"] for book in embedded_books]
        isbn_list = [book["isbn13"] for book in embedded_books]
        
        # Add texts to existing collection
        vector_store.add_texts(texts)
        print(f"Added {len(texts)} embeddings to Qdrant")
        
        # Mark books as processed in Supabase
        for isbn in isbn_list:
            supabase.table("books").update({"needs_embedding": False}).eq("isbn13", isbn).execute()
        
        print(f"Marked {len(isbn_list)} books as processed")

    # Define task dependencies
    books = extract()
    embeddings = transform(books)
    load(embeddings)

update_embeddings_dag()

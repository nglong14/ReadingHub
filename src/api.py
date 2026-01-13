import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest, SearchResponse, BookResponse
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(
    title="Book Recommendation API",
    description="API for book recommendation system",
    version="1.0.0"
)

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_books = None 
embedding = None
books_df = None

@app.on_event("startup")
async def load_resources():
    global db_books, embedding, books_df

    qdrant_storage_path = "../qdrant_storage"
    models_cache_path = "../models"
    
    # Fetch all books data from Supabase using pagination
    # Supabase has a default limit of 1000, so we need to paginate
    books_data = []
    page_size = 1000
    offset = 0
    
    while True:
        response = supabase.table("books").select("*").range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        books_data.extend(response.data)
        if len(response.data) < page_size:
            break
        offset += page_size
    
    # print(f"Fetched {len(books_data)} books from Supabase")

    if not os.path.exists(qdrant_storage_path):
        raise FileNotFoundError(f"Qdrant storage not found at {qdrant_storage_path}")
    
    if not os.path.exists(models_cache_path):
        raise FileNotFoundError(f"Models cache not found at {models_cache_path}")
    
    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        cache_folder=models_cache_path,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # Initialize Qdrant client and load collection
    client = QdrantClient(path=qdrant_storage_path)
    
    db_books = QdrantVectorStore(
        client=client,
        collection_name="books",
        embedding=embedding
    )

    # Convert Supabase data to DataFrame
    books_df = pd.DataFrame(books_data)
    print(books_df.shape)

@app.get("/")
async def root():
    return {"message": "Book Recommendation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database_status": db_books is not None}

@app.post("/search", response_model=SearchResponse)
async def search_books(request: SearchRequest):
    if db_books is None or books_df is None:
        raise HTTPException(status_code=503, detail="Resources not loaded")
    #Handle request query 
    try:
        docs_with_scores = db_books.similarity_search_with_score(request.query, k=request.top_k)
        results = []
        for doc, score in docs_with_scores:
            isbn_str = doc.page_content.strip('"').split()[0]
            try:
                isbn = int(isbn_str)
                book_data = books_df[books_df["isbn13"] == isbn]
                
                if not book_data.empty:
                    book = book_data.iloc[0]
                    results.append(BookResponse(
                        isbn13=str(book.get("isbn13", "")),
                        title=book.get("title", ""),
                        authors=book.get("authors", ""),
                        categories=book.get("categories", ""),
                        description=book.get("description", ""),
                        thumbnail=book.get("thumbnail", ""),
                        average_rating=float(book.get("average_rating", 0)) if pd.notna(book.get("average_rating")) else None,
                        num_pages=int(book.get("num_pages", 0)) if pd.notna(book.get("num_pages")) else None,
                        published_year=int(book.get("published_year", 0)) if pd.notna(book.get("published_year")) else None,
                        score=float(score),
                        anger=float(book.get("anger", 0)) if pd.notna(book.get("anger")) else None,
                        disgust=float(book.get("disgust", 0)) if pd.notna(book.get("disgust")) else None,
                        fear=float(book.get("fear", 0)) if pd.notna(book.get("fear")) else None,
                        joy=float(book.get("joy", 0)) if pd.notna(book.get("joy")) else None,
                        sadness=float(book.get("sadness", 0)) if pd.notna(book.get("sadness")) else None,
                        surprise=float(book.get("surprise", 0)) if pd.notna(book.get("surprise")) else None,
                        neutral=float(book.get("neutral", 0)) if pd.notna(book.get("neutral")) else None,
                    ))
            except (ValueError, IndexError):
                continue
        
        return SearchResponse(results=results, total=len(results))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
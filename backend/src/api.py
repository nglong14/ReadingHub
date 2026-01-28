import os
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest, SearchResponse, BookResponse, CreateBook, CreateBookResponse
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase._async.client import AsyncClient, create_client as async_create_client
from utils.cache import CachedSearch, EmbeddingCache

load_dotenv()

app = FastAPI(
    title="Book Recommendation API",
    description="API for book recommendation system",
    version="1.0.0"
)

supabase: AsyncClient = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://reading-hub-swart.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_books = None 
embedding = None
books_df = None
search_cache = None
embedding_cache = None

@app.on_event("startup")
async def load_resources():
    global db_books, embedding, books_df, search_cache, embedding_cache, supabase

    # Initialize async Supabase client
    supabase = await async_create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Fetch all books data from Supabase using pagination
    # Supabase has a default limit of 1000
    books_data = []
    page_size = 1000
    offset = 0
    
    while True:
        response = await supabase.table("books").select("*").range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        books_data.extend(response.data)
        if len(response.data) < page_size:
            break
        offset += page_size
    
    # print(f"Fetched {len(books_data)} books from Supabase")

    # HuggingFace will auto-download model to default cache if not present
    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # Initialize Qdrant Cloud client
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    
    db_books = QdrantVectorStore(
        client=client,
        collection_name="books",
        embedding=embedding
    )

    # Convert Supabase data to DataFrame
    books_df = pd.DataFrame(books_data)
    print(books_df.shape)

    # Initialize Redis caches
    search_cache = CachedSearch()
    embedding_cache = EmbeddingCache()

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
        params = {"top_k": request.top_k}
        cached_results = search_cache.get(request.query, params)

        if cached_results:
            return SearchResponse(
                results=[BookResponse(**r) for r in cached_results],
                total=len(cached_results)
            )

        # Check for cached embedding first
        query_embedding = embedding_cache.get(request.query)
        if query_embedding is None:
            # Generate and cache the embedding
            query_embedding = embedding.embed_query(request.query)
            embedding_cache.set(request.query, query_embedding)
        
        # Use the embedding for vector search
        docs_with_scores = db_books.similarity_search_with_score_by_vector(query_embedding, k=request.top_k)
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
        
        # Cache the results before returning
        search_cache.set(request.query, params, [r.model_dump() for r in results])
        return SearchResponse(results=results, total=len(results))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        user_response = await supabase.auth.get_user(token)
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.post("/create", response_model=CreateBookResponse)
async def create_book(book: CreateBook, user = Depends(get_current_user)):
    try:
        book_data = book.model_dump()
        book_data["created_by"] = user.id
        book_data["tagged_description"] = f"{book_data['isbn13']} {book_data['description']}"
        await supabase.table("books").insert(book_data).execute()
        return CreateBookResponse(**book_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create book failed: {str(e)}")

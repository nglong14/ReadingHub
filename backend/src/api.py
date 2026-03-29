import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest, SearchResponse, BookResponse, CreateBook, CreateBookResponse
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from supabase._async.client import AsyncClient, create_client as async_create_client
from utils.cache import CachedSearch, EmbeddingCache
from utils.batch_encoder import BatchEncoder

load_dotenv()

# Global resources — initialised in lifespan
supabase: AsyncClient = None
model: SentenceTransformer = None
client: QdrantClient = None
search_cache: CachedSearch = None
embedding_cache: EmbeddingCache = None
batch_encoder: BatchEncoder = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, model, search_cache, embedding_cache, supabase, batch_encoder
    supabase = await async_create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    search_cache = CachedSearch()
    embedding_cache = EmbeddingCache()
    batch_encoder = BatchEncoder(model=model, max_batch_size=32, max_wait_ms=50)
    batch_encoder.start()
    yield
    await batch_encoder.stop()


app = FastAPI(
    title="Book Recommendation API",
    description="API for book recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://reading-hub-swart.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Book Recommendation API is running"}


@app.get("/health")
async def health_check():
    redis_ok = (
        search_cache is not None and search_cache.is_healthy()
        and embedding_cache is not None and embedding_cache.is_healthy()
    )
    return {
        "status": "healthy",
        "qdrant": client is not None,
        "redis": redis_ok,
    }


@app.post("/search", response_model=SearchResponse)
async def search_books(request: SearchRequest):
    if client is None:
        raise HTTPException(status_code=503, detail="Resources not loaded")

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
            query_embedding = await batch_encoder.submit(request.query)
            embedding_cache.set(request.query, query_embedding)

        # Direct Qdrant search — reads metadata from point payloads
        hits = client.query_points(
            collection_name="books",
            query=query_embedding,
            limit=request.top_k,
            with_payload=True,
        ).points

        results = []
        for hit in hits:
            payload = hit.payload
            try:
                results.append(BookResponse(
                    isbn13=str(payload.get("isbn13", "")),
                    title=payload.get("title", ""),
                    authors=payload.get("authors", ""),
                    categories=payload.get("categories", ""),
                    description=payload.get("description", ""),
                    thumbnail=payload.get("thumbnail", ""),
                    average_rating=float(payload["average_rating"]) if payload.get("average_rating") is not None else None,
                    num_pages=int(payload["num_pages"]) if payload.get("num_pages") is not None else None,
                    published_year=int(payload["published_year"]) if payload.get("published_year") is not None else None,
                    score=float(hit.score),
                    anger=float(payload["anger"]) if payload.get("anger") is not None else None,
                    disgust=float(payload["disgust"]) if payload.get("disgust") is not None else None,
                    fear=float(payload["fear"]) if payload.get("fear") is not None else None,
                    joy=float(payload["joy"]) if payload.get("joy") is not None else None,
                    sadness=float(payload["sadness"]) if payload.get("sadness") is not None else None,
                    surprise=float(payload["surprise"]) if payload.get("surprise") is not None else None,
                    neutral=float(payload["neutral"]) if payload.get("neutral") is not None else None,
                ))
            except Exception:
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
async def create_book(book: CreateBook, user=Depends(get_current_user)):
    try:
        book_data = book.model_dump()
        book_data["created_by"] = user.id
        book_data["tagged_description"] = f"{book_data['isbn13']} {book_data['description']}"
        await supabase.table("books").insert(book_data).execute()
        return CreateBookResponse(**book_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create book failed: {str(e)}")

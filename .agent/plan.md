# ReadingHub Infra Upgrade — Agent Execution Plan

## Context
This is a FastAPI-based book recommendation system. The codebase currently uses LangChain as an abstraction layer over sentence-transformers and Qdrant. The goal is to remove LangChain entirely from the critical request path, fix deprecated patterns and add observability.

The main file is `main.py`. All changes below are surgical and ordered by dependency — complete each task fully before moving to the next.

---

## Current Dependencies to be Aware Of
- `langchain_huggingface.HuggingFaceEmbeddings` — wraps sentence-transformers, must be replaced
- `langchain_qdrant.QdrantVectorStore` — wraps qdrant-client, must be replaced
- `qdrant_client.QdrantClient` — already imported, keep and use directly
- `@app.on_event("startup")` — deprecated FastAPI pattern, must be replaced with lifespan

---

## Task 1 — Replace HuggingFaceEmbeddings with SentenceTransformer directly

### Files to modify
- `main.py`
- `requirements.txt`

### Instructions
1. Remove the import: `from langchain_huggingface import HuggingFaceEmbeddings`
2. Add the import: `from sentence_transformers import SentenceTransformer`
3. Replace the embedding initialization block:
```python
# REMOVE this
embedding = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# ADD this
model = SentenceTransformer("all-MiniLM-L6-v2")
```
4. In the `/search` endpoint, replace the embedding call:
```python
# REMOVE this
query_embedding = await embedding.embed_query(request.query)

# ADD this
query_embedding = model.encode(request.query, normalize_embeddings=True).tolist()
```
5. In `requirements.txt`, remove `langchain-huggingface` and add `sentence-transformers` if not already present.

### Validation
- The `/search` endpoint must return results identical to before
- No import from any `langchain` package should remain for embedding

---

## Task 2 — Replace QdrantVectorStore with direct qdrant-client search

### Files to modify
- `main.py`

### Instructions
1. Remove the import: `from langchain_qdrant import QdrantVectorStore`
2. Remove the `QdrantVectorStore` initialization:
```python
# REMOVE this
db_books = QdrantVectorStore(
    client=client,
    collection_name="books",
    embedding=embedding
)
```
3. Keep the raw `QdrantClient` instance as `client`.
4. In the `/search` endpoint, replace the LangChain search call with a direct Qdrant search:
```python
# REMOVE this
docs_with_scores = db_books.similarity_search_with_score_by_vector(query_embedding, k=request.top_k)

# ADD this
hits = client.search(
    collection_name="books",
    query_vector=query_embedding,
    limit=request.top_k,
    with_payload=True
)
```
5. Replace the result parsing loop. The new loop reads metadata from `hit.payload` instead of parsing `doc.page_content` and scanning the DataFrame:
```python
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
```
6. Remove all references to `db_books`, `books_df`, and the Supabase pagination fetch at startup. The serving layer no longer needs book metadata in memory — it reads from Qdrant payloads.
7. Remove the global variables `db_books` and `books_df`.

### Prerequisite
Before this works, the Qdrant collection must have full book metadata stored in each point's payload. If it does not, update the Airflow indexing DAG to upsert payloads like this:
```python
from qdrant_client.models import PointStruct

client.upsert(
    collection_name="books",
    points=[
        PointStruct(
            id=idx,
            vector=vector,
            payload={
                "isbn13": row["isbn13"],
                "title": row["title"],
                "authors": row["authors"],
                "categories": row["categories"],
                "description": row["description"],
                "thumbnail": row["thumbnail"],
                "average_rating": row.get("average_rating"),
                "num_pages": row.get("num_pages"),
                "published_year": row.get("published_year"),
                "anger": row.get("anger"),
                "disgust": row.get("disgust"),
                "fear": row.get("fear"),
                "joy": row.get("joy"),
                "sadness": row.get("sadness"),
                "surprise": row.get("surprise"),
                "neutral": row.get("neutral"),
            }
        )
        for idx, (row, vector) in enumerate(zip(rows, vectors))
    ]
)
```

### Validation
- No import from any `langchain` package should remain for vector search
- `/search` returns correct results with all fields populated from payload
- Startup no longer fetches from Supabase or loads a DataFrame

---

## Task 3 — Replace deprecated startup event with FastAPI lifespan

### Files to modify
- `main.py`

### Instructions
1. Add to imports: `from contextlib import asynccontextmanager`
2. Define the lifespan context manager before `app = FastAPI(...)`:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, model, search_cache, embedding_cache, supabase
    supabase = await async_create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    search_cache = CachedSearch()
    embedding_cache = EmbeddingCache()
    yield
```
3. Pass it into the FastAPI constructor:
```python
app = FastAPI(
    title="Book Recommendation API",
    description="API for book recommendation system",
    version="1.0.0",
    lifespan=lifespan
)
```
4. Remove the old `@app.on_event("startup")` decorated function entirely.

### Validation
- Server starts without deprecation warnings
- All global resources (`model`, `client`, `search_cache`, `embedding_cache`) are available on first request

---


## Task 4 — Clean up requirements.txt

### Files to modify
- `requirements.txt`

### Instructions
Remove all LangChain packages:
```
langchain
langchain-core
langchain-community
langchain-huggingface
langchain-qdrant
```

Ensure these are present:
```
fastapi
uvicorn
sentence-transformers
qdrant-client
redis
supabase
prometheus-client
python-dotenv
```

Remove `pandas` only if `books_df` has been fully eliminated. If pandas is used anywhere else in the codebase, keep it.

### Validation
- `pip install -r requirements.txt` completes without errors
- No `langchain` package appears in `pip list`
- Application starts and all endpoints respond correctly

---

## Final Validation Checklist

Run these checks in order after all tasks are complete:

- [ ] `grep -r "langchain" .` returns no results inside any `.py` file
- [ ] `GET /health` returns `{"status": "healthy"}`
- [ ] `POST /search` with a sample query returns correct results with all fields populated
- [ ] `GET /metrics` returns Prometheus-formatted text with all four metric names present
- [ ] Server startup logs show no deprecation warnings
- [ ] Global variables `db_books` and `books_df` are gone entirely
- [ ] Remaining globals are only: `model`, `client`, `search_cache`, `embedding_cache`, `supabase`

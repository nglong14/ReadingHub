import os
from fastapi import FastAPI, HTTPException
from models import SearchRequest, SearchResponse, BookResponse
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# app = FastAPI()


app = FastAPI(
    title="Book Recommendation API",
    description="API for book recommendation system",
    version="1.0.0"
)

db_books = None 
embedding = None
books_df = None

@app.on_event("startup")
async def load_resources():
    global db_books, embedding, books_df

    faiss_index_path = "./faiss_index"
    models_cache_path = "./models"
    books_csv_path = "books_with_emotions.csv"

    if not os.path.exists(faiss_index_path):
        raise FileNotFoundError(f"FAISS index not found at {faiss_index_path}")
    
    if not os.path.exists(models_cache_path):
        raise FileNotFoundError(f"Models cache not found at {models_cache_path}")
    
    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        cache_folder=models_cache_path,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    db_books = FAISS.load_local(faiss_index_path, embedding, allow_dangerous_deserialization=True)

    books_df = pd.read_csv(books_csv_path)

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
                        score=float(score)
                    ))
            except (ValueError, IndexError):
                continue
        
        return SearchResponse(results=results, total=len(results))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
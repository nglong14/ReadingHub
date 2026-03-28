"""
One-time backfill script: writes full book metadata into existing Qdrant point payloads.

This does NOT delete or re-embed any vectors — it only adds payload fields to
points that were originally indexed without metadata (via LangChain from_documents).

Usage:
    cd d:/BookRecommendation/backend
    python src/origin/backfill_qdrant_payloads.py
"""
import os
import re
import sys
from dotenv import load_dotenv
from supabase import create_client
from qdrant_client import QdrantClient

load_dotenv()

COLLECTION_NAME = "books"
SUPABASE_PAGE_SIZE = 1000
QDRANT_BATCH_SIZE = 256


def fetch_all_books(supabase) -> dict:
    """Fetch all books from Supabase and return as a dict keyed by isbn13."""
    books_by_isbn = {}
    offset = 0
    while True:
        response = (
            supabase.table("books")
            .select(
                "isbn13,title,authors,categories,description,thumbnail,"
                "average_rating,num_pages,published_year,"
                "anger,disgust,fear,joy,sadness,surprise,neutral"
            )
            .range(offset, offset + SUPABASE_PAGE_SIZE - 1)
            .execute()
        )
        if not response.data:
            break
        for row in response.data:
            isbn = str(row["isbn13"])
            books_by_isbn[isbn] = row
        if len(response.data) < SUPABASE_PAGE_SIZE:
            break
        offset += SUPABASE_PAGE_SIZE
    return books_by_isbn


def extract_isbn(page_content: str) -> str | None:
    """
    LangChain stored page_content as: '"<isbn13> <description>"'
    (with wrapping escaped quotes). Strip them before matching the ISBN.
    """
    if not page_content:
        return None
    # Strip whitespace, then any leading/trailing quote or backslash characters
    cleaned = page_content.strip().strip('\\"\'')
    match = re.match(r"^(\d{10,13})", cleaned)
    return match.group(1) if match else None


def main():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")

    if not all([supabase_url, supabase_key, qdrant_url, qdrant_key]):
        print("ERROR: Missing required env vars (SUPABASE_URL, SUPABASE_KEY, QDRANT_URL, QDRANT_API_KEY)")
        sys.exit(1)

    print("Connecting to Supabase...")
    supabase = create_client(supabase_url, supabase_key)

    print("Fetching all books from Supabase...")
    books_by_isbn = fetch_all_books(supabase)
    print(f"  Loaded {len(books_by_isbn)} books from Supabase")

    print("Connecting to Qdrant...")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)

    total_points = client.get_collection(COLLECTION_NAME).points_count
    print(f"  Collection '{COLLECTION_NAME}' has {total_points} points")

    matched = 0
    unmatched = 0
    offset = None

    print("\nBackfilling payloads...")
    while True:
        records, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=QDRANT_BATCH_SIZE,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        if not records:
            break

        for record in records:
            payload = record.payload or {}

            # Try to get isbn13 from existing payload first, then fall back to page_content
            isbn = str(payload.get("isbn13", "")) or extract_isbn(payload.get("page_content", ""))

            if not isbn or isbn not in books_by_isbn:
                unmatched += 1
                continue

            book = books_by_isbn[isbn]
            client.set_payload(
                collection_name=COLLECTION_NAME,
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
                points=[record.id],
            )
            matched += 1

        progress = matched + unmatched
        print(f"  Progress: {progress}/{total_points} | matched={matched} unmatched={unmatched}")

        if offset is None:
            break

    print(f"\nDone. Matched: {matched} | Unmatched (no isbn): {unmatched}")
    if unmatched > 0:
        print("  Unmatched points had no recognisable ISBN in page_content.")
        print("  These may be LangChain metadata chunks — safe to ignore if count is small.")


if __name__ == "__main__":
    main()

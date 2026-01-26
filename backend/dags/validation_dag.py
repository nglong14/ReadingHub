import os
import pendulum
from typing import List, Dict
from airflow.sdk import dag, task
from dotenv import load_dotenv


def get_supabase_client():
    """Create and return a Supabase client."""
    from supabase import create_client
    load_dotenv("/mnt/d/BookRecommendation/.env")
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def get_qdrant_client():
    """Create and return a Qdrant client."""
    from qdrant_client import QdrantClient
    return QdrantClient(path="/mnt/d/BookRecommendation/backend/qdrant_storage")


@dag(
    schedule="@weekly",
    start_date=pendulum.datetime(2025, 1, 21, tz="UTC"),
    catchup=False,
    tags=["validation", "books", "health-check"],
)
def validation_dag():
    
    @task()
    def get_supabase_data() -> Dict:
        """Get both count and ISBNs from Supabase in a single task."""
        supabase = get_supabase_client()
        
        # Get count
        count_response = supabase.table("books").select("isbn13", count="exact").execute()
        count = count_response.count or 0
        print(f"Supabase books count: {count}")
        
        # Get all ISBNs
        isbns = []
        page_size = 1000
        offset = 0
        
        while True:
            response = supabase.table("books").select("isbn13").range(offset, offset + page_size - 1).execute()
            if not response.data:
                break
            isbns.extend([book["isbn13"] for book in response.data])
            if len(response.data) < page_size:
                break
            offset += page_size
        
        return {"count": count, "isbns": isbns}
    
    @task()
    def get_qdrant_data() -> Dict:
        """Get both count and ISBNs from Qdrant in a single task to avoid storage locking."""
        qdrant_client = get_qdrant_client()
        
        # Get count
        collection_info = qdrant_client.get_collection("books")
        count = collection_info.points_count
        print(f"Qdrant vectors count: {count}")
        
        # Get all ISBNs
        isbns = []
        offset = None
        
        while True:
            results, offset = qdrant_client.scroll(
                collection_name="books",
                limit=1000,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            if not results:
                break
            for point in results:
                content = point.payload.get("page_content", "")
                try:
                    isbn = int(content.strip('"').split()[0])
                    isbns.append(isbn)
                except (ValueError, IndexError):
                    continue
            if offset is None:
                break
        
        return {"count": count, "isbns": isbns}
    
    @task()
    def find_discrepancies(supabase_isbns: List[int], qdrant_isbns: List[int]) -> Dict:
        supabase_set = set(supabase_isbns)
        qdrant_set = set(qdrant_isbns)
        
        missing_embeddings = list(supabase_set - qdrant_set)
        orphan_vectors = list(qdrant_set - supabase_set)
        
        return {
            "missing_embeddings": missing_embeddings[:20],  # Limit for readability
            "missing_embeddings_count": len(missing_embeddings),
            "orphan_vectors": orphan_vectors[:20],
            "orphan_vectors_count": len(orphan_vectors)
        }
    
    @task()
    def generate_report(
        supabase_count: int,
        qdrant_count: int,
        discrepancies: Dict
    ) -> Dict:
        report = {
            "timestamp": pendulum.now().to_iso8601_string(),
            "supabase_books": supabase_count,
            "qdrant_vectors": qdrant_count,
            "count_diff": supabase_count - qdrant_count,
            "missing_embeddings_count": discrepancies["missing_embeddings_count"],
            "orphan_vectors_count": discrepancies["orphan_vectors_count"],
            "sample_missing": discrepancies["missing_embeddings"],
            "sample_orphans": discrepancies["orphan_vectors"],
            "status": "OK" if discrepancies["missing_embeddings_count"] == 0 and discrepancies["orphan_vectors_count"] == 0 else "ISSUES_FOUND"
        }
        
        print("=" * 50)
        print("VALIDATION REPORT")
        print("=" * 50)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Supabase Books: {report['supabase_books']}")
        print(f"Qdrant Vectors: {report['qdrant_vectors']}")
        print(f"Count Difference: {report['count_diff']}")
        print(f"Missing Embeddings: {report['missing_embeddings_count']}")
        print(f"Orphan Vectors: {report['orphan_vectors_count']}")
        print(f"Status: {report['status']}")
        print("=" * 50)
        
        return report

    # Task dependencies - Supabase and Qdrant tasks can run in parallel
    # but each source's operations are now in a single task to avoid locking
    supabase_data = get_supabase_data()
    qdrant_data = get_qdrant_data()
    
    discrepancies = find_discrepancies(supabase_data["isbns"], qdrant_data["isbns"])
    generate_report(supabase_data["count"], qdrant_data["count"], discrepancies)

validation_dag()

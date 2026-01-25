import os
import pendulum
from typing import List, Dict
from supabase import create_client, Client
from airflow.sdk import dag, task
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv("/mnt/d/BookRecommendation/.env")

# Initialize clients
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
qdrant_client = QdrantClient(path="/mnt/d/BookRecommendation/backend/qdrant_storage")

@dag(
    schedule="@weekly",
    start_date=pendulum.datetime(2025, 1, 21, tz="UTC"),
    catchup=False,
    tags=["validation", "books", "health-check"],
)
def validation_dag():
    
    @task()
    def count_supabase_books() -> int:
        response = supabase.table("books").select("isbn13", count="exact").execute()
        count = response.count or 0
        print(f"Supabase books count: {count}")
        return count
    
    @task()
    def count_qdrant_vectors() -> int:
        collection_info = qdrant_client.get_collection("books")
        count = collection_info.points_count
        print(f"Qdrant vectors count: {count}")
        return count
    
    @task()
    def get_supabase_isbns() -> List[int]:
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
        
        return isbns
    
    @task()
    def get_qdrant_isbns() -> List[int]:
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
        
        return isbns
    
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

    # Task dependencies
    supabase_count = count_supabase_books()
    qdrant_count = count_qdrant_vectors()
    supabase_isbns = get_supabase_isbns()
    qdrant_isbns = get_qdrant_isbns()
    discrepancies = find_discrepancies(supabase_isbns, qdrant_isbns)
    generate_report(supabase_count, qdrant_count, discrepancies)

validation_dag()

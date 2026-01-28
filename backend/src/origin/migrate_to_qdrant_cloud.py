"""
Migration script to copy data from local Qdrant storage to Qdrant Cloud.
Run this script once to migrate all existing vectors.
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

# Configuration
LOCAL_QDRANT_PATH = "../qdrant_storage"
COLLECTION_NAME = "books"
BATCH_SIZE = 100

# Cloud configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


def migrate_to_cloud():
    """Migrate all vectors from local Qdrant to Qdrant Cloud."""
    
    print("=" * 60)
    print("Qdrant Migration: Local → Cloud")
    print("=" * 60)
    
    # Connect to local Qdrant
    print("\n1. Connecting to local Qdrant...")
    local_client = QdrantClient(path=LOCAL_QDRANT_PATH)
    
    # Connect to Qdrant Cloud
    print("2. Connecting to Qdrant Cloud...")
    cloud_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    
    # Get local collection info
    print(f"\n3. Reading local collection '{COLLECTION_NAME}'...")
    local_collection = local_client.get_collection(COLLECTION_NAME)
    
    # Handle both dict and object-based vector config
    vectors_config = local_collection.config.params.vectors
    if isinstance(vectors_config, dict):
        # Named vectors - get size from first vector config
        first_config = next(iter(vectors_config.values()))
        vector_size = first_config.size if hasattr(first_config, 'size') else first_config['size']
    else:
        vector_size = vectors_config.size
    
    points_count = local_collection.points_count
    
    print(f"   - Vector size: {vector_size}")
    print(f"   - Total points: {points_count}")
    
    # Check if cloud collection exists
    collections = cloud_client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME in collection_names:
        print(f"\n4. Collection '{COLLECTION_NAME}' already exists in cloud.")
        response = input("   Do you want to recreate it? (y/n): ").strip().lower()
        if response == 'y':
            cloud_client.delete_collection(COLLECTION_NAME)
            print(f"   Deleted existing collection.")
        else:
            print("   Aborting migration.")
            return
    
    # Create collection in cloud
    print(f"\n5. Creating collection '{COLLECTION_NAME}' in cloud...")
    cloud_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )
    print(f"   Collection created successfully!")
    
    # Migrate data in batches
    print(f"\n6. Migrating {points_count} vectors...")
    migrated = 0
    offset = None
    
    while True:
        # Scroll through local data
        results, offset = local_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=BATCH_SIZE,
            offset=offset,
            with_payload=True,
            with_vectors=True
        )
        
        if not results:
            break
        
        # Convert Record objects to PointStruct for upsert
        points_to_upsert = [
            PointStruct(
                id=record.id,
                vector=record.vector,
                payload=record.payload
            )
            for record in results
        ]
        
        # Upsert to cloud
        cloud_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upsert
        )
        
        migrated += len(results)
        print(f"   Migrated {migrated}/{points_count} vectors ({100*migrated//points_count}%)")
        
        if offset is None:
            break
    
    # Verify migration
    print(f"\n7. Verifying migration...")
    cloud_collection = cloud_client.get_collection(COLLECTION_NAME)
    cloud_count = cloud_collection.points_count
    
    print(f"   - Local points: {points_count}")
    print(f"   - Cloud points: {cloud_count}")
    
    if cloud_count == points_count:
        print("\n✅ Migration completed successfully!")
        print(f"\nYour data is now available at:")
        print(f"   {QDRANT_URL}")
    else:
        print(f"\n⚠️ Warning: Point count mismatch!")
        print(f"   Expected: {points_count}, Got: {cloud_count}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("Error: QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        exit(1)
    
    migrate_to_cloud()

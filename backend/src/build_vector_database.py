import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os

# Create necessary directories
os.makedirs("./qdrant_storage", exist_ok=True)
os.makedirs("./models", exist_ok=True)

#Load data
books = pd.read_csv("../notebooks/books_with_emotions.csv")

raw_documents = TextLoader("../notebooks/tagged_description.txt", encoding="utf-8").load()

#Split documents
text_splitter = CharacterTextSplitter(
        chunk_size=1,
        chunk_overlap=0, 
        separator="\n"
)

documents = text_splitter.split_documents(raw_documents)

embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        cache_folder="./models",
        model_kwargs={'device': 'cpu'},  # Force CPU for deployment
        encode_kwargs={'normalize_embeddings': True}  # Better similarity scores
    )

#Build Qdrant vector store
db_books = QdrantVectorStore.from_documents(
        documents,
        embedding,
        path="./qdrant_storage",
        collection_name="books",
        force_recreate=True
    )

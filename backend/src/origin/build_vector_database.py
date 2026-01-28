import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()

# Create models directory
os.makedirs("./models", exist_ok=True)

# Qdrant Cloud configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

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

# Initialize Qdrant Cloud client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

#Build Qdrant vector store on cloud
db_books = QdrantVectorStore.from_documents(
        documents,
        embedding,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name="books",
        force_recreate=True
    )

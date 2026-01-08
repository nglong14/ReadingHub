import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os

# Create necessary directories
os.makedirs("./faiss_index", exist_ok=True)
os.makedirs("./models", exist_ok=True)

#Load data
books = pd.read_csv("books_with_emotions.csv")

raw_documents = TextLoader("tagged_description.txt", encoding="utf-8").load()

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

#Build FAISS
db_books = FAISS.from_documents(
        documents,
        embedding
    )

db_books.save_local("./faiss_index")
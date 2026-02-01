FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace model during build to avoid 429 rate limiting
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . /app

# Set working directory to src so imports work correctly
WORKDIR /app/src

ENV PORT=8080
# Prevent HuggingFace from attempting downloads at runtime
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

CMD uvicorn api:app --host 0.0.0.0 --port $PORT
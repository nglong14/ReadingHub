# Book Recommendation System

## Overview
This project is a full-stack book recommendation engine that leverages semantic search to help users find books based on natural language queries. It combines a modern React frontend with a robust FastAPI backend, utilizing vector embeddings for intelligent search results.

## Technology Stack

### Frontend
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **State/Auth**: Supabase Client

### Backend
- **Framework**: FastAPI
- **Vector Database**: Qdrant (for semantic search)
- **Database**: Supabase (PostgreSQL for metadata and user data)
- **ML Models**: HuggingFace transformers (`all-MiniLM-L6-v2`) for text embeddings
- **Caching**: Custom Redis-based caching implementation
- **Orchestration**: Apache Airflow (DAGs for data pipelines)

## Features
- **Semantic Search**: Find books by describing plot, mood, or context rather than just keywords.
- **User Authentication**: Secure sign-up and login via Supabase.
- **Book Management**: Authenticated users can add new books to the database.
- **Responsive Design**: Modern interface built with Tailwind CSS.

## Project Structure
- `backend/`: Contains the FastAPI application, Airflow DAGs, and Docker configuration.
- `frontend/`: Contains the React application.
- `models/`: Directory for ML models.
- `notebooks/`: Jupyter notebooks for data exploration and testing.

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js & npm
- Docker (optional, for containerization)
- Redis server (running locally or remotely)
- Apache Airflow (for pipeline orchestration)
- Supabase account
- Qdrant account

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in a `.env` file (refer to `.env.example`).
   - Ensure `REDIS_HOST` and `REDIS_PORT` are set correctly.
5. Run the server:
   ```bash
   uvicorn src.api:app --reload
   ```

### Airflow Pipeline Setup
1. Ensure your Airflow environment is active.
2. Point Airflow to the `backend/dags` directory.
3. Available DAGs:
   - `update_embeddings_dag`: Updates vector embeddings for new books.
   - `validation_dag`: Validates system integrity and data consistency.

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables (if required).
4. Start the development server:
   ```bash
   npm run dev
   ```

## API Documentation
Once the backend is running, you can access the interactive API documentation at `http://localhost:8000/docs`.

# ReadingHub

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Installation & Setup](#installation--setup)
- [Contact](#contact)

## Overview
ReadingHub is a full-stack book recommendation engine designed to solve the limitations of traditional keyword-based search. 

**The Problem:** Traditional search engines require users to know exact titles, author names, or specific keywords to find a book. When a user only remembers the "vibe," a vague plot detail, or a specific emotional tone of a book, keyword-based search fails. 

**The Solution:** ReadingHub leverages Natural Language Processing (NLP) and Vector Search technology to provide Semantic Search. It matches queries based on semantic meaning and context rather than exact text overlap.

## Features
*   **Semantic Search Engine:** Find books by describing the plot, emotional tone, or genre using natural language.
*   **Intelligent Recommendations:** Get highly accurate book suggestions powered by vector similarity scoring.
*   **User Authentication:** Secure user registration and login functionality provided by Supabase.
*   **Library Management:** Authenticated users can submit and add new books to the global database.
*   **Automated Data Ingestion:** Background pipelines automatically generate embeddings for newly added books.
*   **High-Speed Response:** Multi-tier caching system ensuring rapid search results and minimal API latency.
*   **Responsive UI:** A clean, modern interface accessible on both desktop and mobile devices.

## Project Structure
The repository is structured to separate concerns between the user interface, backend APIs, data pipelines, and machine learning models.

*   `backend/`: The core API server and data orchestration layer.
    *   `src/`: Contains the FastAPI application, routing logic, and caching integrations.
    *   `dags/`: Apache Airflow Directed Acyclic Graphs used for asynchronous data pipelines and embedding updates.
    *   `Dockerfile`: Containerization configuration for deployable backend services.
*   `frontend/`: The user-facing application built with React, Vite, and Tailwind CSS.
    *   `src/services/`: API integration layer bridging the React app with the FastAPI backend.
*   `models/`: Directory dedicated to storing pre-trained HuggingFace sentence transformers locally.
*   `notebooks/`: Jupyter notebooks used during the research phase for data exploration, model testing, and data cleaning.

## Technologies Used
**Frontend Layer**
*   **React (Vite):** A fast frontend build tool and library for constructing the user interface.
*   **Tailwind CSS:** A utility-first CSS framework for responsive design.
*   **Supabase Client:** Handles user authentication and session management directly from the browser.

**Backend & ML Layer**
*   **FastAPI:** A high-performance web framework for Python, used to serve the core search APIs.
*   **HuggingFace Transformers (`all-MiniLM-L6-v2`):** A lightweight, fast NLP model used to generate 384-dimensional vector embeddings from text descriptions. It is optimized to run inference entirely on CPU.
*   **Qdrant Vector Database:** A high-performance, Rust-based vector search engine utilizing the HNSW (Hierarchical Navigable Small World) algorithm to perform sub-millisecond similarity searches.
    *   **Top-K Retrieval Logic:** Instead of performing a brute-force scan, the system leverages Qdrant's HNSW graph to rapidly navigate and locate the `Top-K` nearest neighbors. By passing `k=request.top_k` via Langchain, we delegate the entire sorting and filtering process to the database, achieving logarithmic $O(\log N)$ search latency.
*   **Redis:** An in-memory data store providing a multi-tier caching strategy to store frequent search queries and computed embeddings, reducing API latency.

**Data & Infrastructure Layer**
*   **Supabase (PostgreSQL):** The primary relational database storing user information, book metadata, and authentication records.
*   **Apache Airflow:** The workflow orchestration platform responsible for extracting new books from Supabase, transforming them through the embedding model, and loading them into Qdrant asynchronously.

## Installation & Setup

### Prerequisites
*   Python 3.11+
*   Node.js & npm
*   Redis server (running locally or accessible via network)
*   Apache Airflow instance
*   Supabase account and project credentials
*   Qdrant account and API credentials

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment.
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and configure your credentials:
   ```bash
   cp .env.example .env
   ```
   Ensure you provide valid values for `SUPABASE_URL`, `SUPABASE_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `REDIS_HOST`, and `REDIS_PORT`.
5. Start the FastAPI development server:
   ```bash
   uvicorn src.api:app --reload
   ```
   The API will be accessible at `http://localhost:8000`. The interactive Swagger documentation is available at `http://localhost:8000/docs`.

### Airflow Pipeline Setup
1. Ensure your Airflow environment is initialized and running.
2. Point Airflow's DAGs folder to the `backend/dags` directory of this project.
3. Configure your Airflow connections to match the credentials in your `.env` file.
4. Enable the `update_embeddings_dag` in the Airflow UI to begin processing new book entries.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the necessary Node packages:
   ```bash
   npm install
   ```
3. Create a `.env` file in the frontend directory (if required) to set VITE prefix variables for your API URLs.
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The web application will be accessible at `http://localhost:5173`.

## Contact
Maintainer: nglong14
Project Repository: [GitHub Link / Organization Link]

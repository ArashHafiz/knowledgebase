# Knowledge Base API

A Python-based document storage and retrieval system built with **FastAPI, SQLAlchemy, and SQLite**. The project allows users to upload text documents, store their contents and metadata in a database, retrieve individual documents, and search for relevant passages using keywords or natural-language questions.

## Features

- **Document ingestion:** Upload UTF-8 text files through a REST API.
- **Persistent storage:** Store document contents and metadata in a SQLite database using SQLAlchemy.
- **Document management:** List uploaded documents and retrieve individual documents by ID.
- **Keyword search:** Find documents containing a specified keyword and return matching lines.
- **Basic relevance ranking:** Rank matching lines by keyword frequency and documents using a custom scoring formula.
- **Question-based retrieval:** Extract keywords from a question, filter common stop words, and retrieve matching passages.
- **Document metadata:** Track filenames, unique document IDs, word counts, line counts, and timestamps.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | REST API development |
| SQLAlchemy | ORM and database operations |
| SQLite | Persistent document storage |
| Uvicorn | ASGI server for running the API |

## Project Structure

```text
knowledgebase/
├── main.py              # API endpoints and retrieval logic
├── models.py            # SQLAlchemy database models
├── database.py          # Database engine, sessions, and initialization
├── knowledgebase.db     # SQLite database (created at runtime)
└── .venv/               # Python virtual environment
```

The SQLite database and virtual environment are local runtime files and do not necessarily need to be committed to version control.

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip

### 1. Clone the repository

```bash
git clone <repository-url>
cd knowledgebase
```

Replace `<repository-url>` with the URL of this repository.

### 2. Create and activate a virtual environment

**Windows (Command Prompt):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install fastapi uvicorn sqlalchemy python-multipart
```

### 4. Start the API server

```bash
python -m uvicorn main:app --reload
```

The API will be available at:

- **API base URL:** http://127.0.0.1:8000
- **Interactive API documentation (Swagger):** http://127.0.0.1:8000/docs

FastAPI initializes the database when the application starts. SQLite creates the database file and document table if they do not already exist.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/documents` | List documents and their metadata |
| `GET` | `/documents/{doc_id}` | Retrieve a document by its ID |
| `GET` | `/search?query={keyword}` | Search document contents for a keyword |
| `POST` | `/ask?question={question}` | Extract keywords from a question and retrieve matching passages |
| `POST` | `/upload` | Upload and store a text document |

### Upload a document

Use `POST /upload` to upload a UTF-8 `.txt` file as multipart form data, with the file field named `file`.

The API stores the filename, text content, word count, line count, and creation timestamp. Each document receives a unique database ID, allowing multiple documents to share the same filename.

### Search documents

Use `GET /search` with a query parameter:

```text
/search?query=brezhnev
```

The response contains matching documents, relevant lines, match counts, and document-level relevance scores.

Search is currently case-insensitive and uses substring matching. For example, a query may match a term even when it appears within a longer word.

### Retrieve passages from a question

Use `POST /ask` with a question parameter:

```text
/ask?question=When%20did%20Brezhnev%20die
```

The endpoint lowercases the question, removes punctuation, splits it into keywords, filters common stop words, and searches for each remaining keyword.

The current implementation returns separate search results for individual keywords. It does not yet generate natural-language answers.

## Database Design

The `Document` model maps to the SQLite `documents` table.

| Field | Description |
|---|---|
| `id` | Auto-incrementing primary key |
| `filename` | Original filename |
| `content` | Full text content |
| `date_added` | Record creation timestamp |
| `word_count` | Number of whitespace-separated tokens |
| `line_count` | Number of lines |

SQLAlchemy manages database queries and transactions, while SQLite provides persistent local storage.

## Current Limitations

- Only UTF-8 text content is processed, and no check that documents are in UTF-8 format has been implemented yet; PDF and other document formats are not yet supported.
- Search relies on keyword matching rather than semantic similarity or vector embeddings.
- Relevance scores use a custom heuristic based on matching lines, matching words, and document length.
- Question-based retrieval performs separate searches for extracted keywords instead of combining all passages into one globally ranked list.
- The application currently scans stored document contents directly, which may become inefficient as the knowledge base grows.
- Database schema changes are not automatically migrated by SQLAlchemy's table-creation mechanism.

## Future Development

Planned improvements include:

- Combining results from multiple keywords into a unified passage-ranking pipeline.
- Deduplicating matching passages and limiting retrieval to the most relevant results.
- Improving relevance scoring and evaluating retrieval quality against representative questions.
- Supporting additional document formats and more robust text extraction.
- Integrating a large language model (LLM) to generate answers grounded in retrieved passages.
- Exploring more scalable retrieval approaches as the knowledge base grows.

## Motivation

This project is an exploration of document ingestion, relational data modelling, API development, and information retrieval. Its longer-term goal is to build a retrieval pipeline that selects relevant information from a personal knowledge base before passing that information to an LLM, rather than relying on an LLM to process entire documents indiscriminately, which would be an inefficient use of tokens especially for large docs/batches.

# Knowledge Base API

A Python-based document storage, retrieval and AI-assisted question-answering system built with **FastAPI, SQLAlchemy, SQLite and Google's Gemini API**.

The project allows users to upload text documents, store their contents and metadata, retrieve individual documents, search for relevant passages, and ask natural-language questions. It uses a custom keyword-based retrieval pipeline to identify relevant passages before passing them to a large language model (LLM) to generate answers grounded in the retrieved information.

## Features

- **Document ingestion:** Upload UTF-8 text files through a REST API.
- **Persistent storage:** Store document contents and metadata in a SQLite database using SQLAlchemy.
- **Document management:** List uploaded documents and retrieve individual documents by ID.
- **Document metadata:** Track filenames, unique document IDs, word counts and creation timestamps.
- **Passage-based processing:** Split document contents into paragraph-based chunks while retaining their original line positions.
- **Keyword search:** Find relevant passages using case-insensitive keyword matching.
- **Relevance ranking:** Rank matching passages using a custom scoring system based on keyword matches and inverse document frequency (IDF).
- **Question-based retrieval:** Extract keywords from natural-language questions, filter common stop words and retrieve relevant passages.
- **AI-assisted question answering:** Use Google's Gemini API to generate natural-language answers based on retrieved passages.
- **Source references:** Return source filenames, document IDs, chunk numbers and line positions alongside generated answers.
- **Grounded responses:** Instruct the LLM to use retrieved information, avoid unsupported claims and acknowledge when the available evidence is insufficient.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | REST API development |
| SQLAlchemy | ORM and database operations |
| SQLite | Persistent document storage |
| Uvicorn | ASGI server |
| Google Gemini API | AI-assisted answer generation |
| Google Gen AI SDK | Gemini API integration |
| python-dotenv | Environment variable management |

## Project Structure

```text
knowledgebase/
├── main.py              # API endpoints and retrieval logic
├── models.py            # SQLAlchemy database models
├── database.py          # Database engine, sessions and initialization
├── ai_service.py        # Gemini API integration and answer generation
├── requirements.txt     # Python dependencies
├── .env                 # API credentials and configuration
├── .gitignore           # Files excluded from version control
├── knowledgebase.db     # SQLite database (created at runtime)
└── .venv/               # Python virtual environment
```

The SQLite database, virtual environment and environment configuration file are local runtime files and should not be committed to version control. In particular, `.env` contains the Gemini API key and must remain private.

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- A Google AI Studio API key

### 1. Clone the repository

```bash
git clone https://github.com/ArashHafiz/knowledgebase
cd knowledgebase
```

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
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace `your_api_key_here` with your Google AI Studio API key.

The model can be changed through the `GEMINI_MODEL` environment variable. The application uses `gemini-3.5-flash-lite` by default if no model is specified.

**Important:** Do not commit your `.env` file or expose your API key in public repositories.

### 5. Start the API server

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
| `GET` | `/search?query={keyword}` | Search document contents and retrieve matching passages |
| `POST` | `/ask?question={question}` | Retrieve relevant passages and generate an AI-assisted answer |
| `POST` | `/upload` | Upload and store a text document |

### Upload a document

Use `POST /upload` to upload a UTF-8 `.txt` file as multipart form data, with the file field named `file`.

The API stores the filename, full text content, word count and creation timestamp. Each document receives a unique database ID, allowing multiple documents to share the same filename.

### Search documents

Use `GET /search` with a query parameter:

```text
/search?query=uranium
```

The search process:

1. Normalises the query by converting it to lowercase and removing punctuation.
2. Splits the query into individual words.
3. Processes stored documents into paragraph-based chunks.
4. Identifies chunks containing the query.
5. Calculates matching-word and document-level relevance scores.
6. Returns matching passages ranked by relevance.

The response includes document identifiers, filenames, chunk numbers, original line positions, matching-word counts and relevance scores.

Search currently uses keyword and substring matching rather than semantic similarity.

### Ask a question

Use `POST /ask` with a natural-language question parameter:

```text
/ask?question=Where%20is%20uranium%20found
```

The question-answering pipeline works as follows:

1. **Question processing:** Normalises the question, extracts keywords and removes common stop words.
2. **Passage retrieval:** Searches the document collection for each extracted keyword.
3. **Relevance ranking:** Uses inverse document frequency (IDF) to give greater weight to keywords appearing in fewer documents.
4. **Passage selection:** Combines matching results, ranks the retrieved passages and selects the five highest-ranked chunks.
5. **Answer generation:** Passes the original question and retrieved passages to the Gemini API.
6. **Source attribution:** Returns the generated answer alongside structured references to the retrieved source passages.

The LLM is instructed to answer using only the retrieved information, avoid unsupported claims and acknowledge when the available evidence is insufficient.

The response contains:

- `answer`: The generated natural-language answer.
- `sources`: A list of retrieved source references, including filenames, document IDs, chunk numbers and line positions.

The retrieval pipeline and LLM integration are kept separate. This allows the retrieval system to be evaluated and improved independently of the language model.

## Database Design

The `Document` model maps to the SQLite `documents` table.

| Field | Description |
|---|---|
| `id` | Auto-incrementing primary key |
| `filename` | Original filename |
| `content` | Full text content |
| `date_added` | Record creation timestamp |
| `word_count` | Number of whitespace-separated tokens |

SQLAlchemy manages database queries and transactions, while SQLite provides persistent local storage.

## Current Limitations

- Only UTF-8 text content is currently supported. PDF and other document formats are not yet supported.
- Search relies on keyword matching rather than semantic similarity or vector embeddings.
- Relevance scores use a custom heuristic and are not calibrated measures of semantic relevance.
- Retrieval processes document contents directly, which may become inefficient as the knowledge base grows.
- The question-answering pipeline selects a fixed maximum of five passages, which may not always provide sufficient context.
- AI-generated answers depend on the quality of retrieved passages and may still contain unsupported claims or inaccurate source citations.
- The application currently uses a local SQLite database and does not yet implement a database migration framework.
- Upload validation, comprehensive error handling and automated test coverage are still being developed.

## Future Development

Planned improvements include:

- Evaluating retrieval quality against a representative dataset of factual, descriptive, multi-part, multi-hop, ambiguous and unsupported questions.
- Improving passage ranking and filtering based on evaluation results.
- Optimising document processing and retrieval performance for larger collections.
- Introducing automated tests for API endpoints, database operations, retrieval and AI integration.
- Improving input validation, error handling and database management.
- Supporting additional document formats and more robust text extraction.
- Developing a dedicated frontend for document management, search and AI-assisted question answering.
- Exploring more scalable retrieval approaches as the knowledge base grows.

## Motivation

This project explores document ingestion, relational data modelling, API development, information retrieval and the integration of large language models into practical applications.

Its central objective is to build a retrieval pipeline that identifies relevant information from a personal knowledge base before passing selected passages to an LLM. Rather than supplying entire documents indiscriminately, the system retrieves a limited amount of relevant context, making more efficient use of model tokens while providing a basis for source-grounded answers.

The longer-term goal is to develop a practical knowledge management application that combines structured document storage, effective information retrieval and AI-assisted access to personal collections of information.
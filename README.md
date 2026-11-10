# Knowledge Base

A full-stack document storage, retrieval and AI-assisted question-answering application. The backend is built with **FastAPI, SQLAlchemy, SQLite and Google's Gemini API**, and the frontend with **React, TypeScript and Vite**.

Users can upload text documents, browse and read them, search for relevant passages, and ask natural-language questions. A custom keyword-based retrieval pipeline selects relevant passages, which are passed to a large language model (LLM) to generate answers grounded in the retrieved information, with references to the sources used.

## Features

### Backend

- **Document ingestion:** Upload UTF-8 text files through a REST API.
- **Persistent storage:** Store document contents and metadata in a SQLite database using SQLAlchemy.
- **Document management:** List uploaded documents and retrieve individual documents by ID.
- **Document metadata:** Track filenames, unique document IDs, word counts and creation timestamps.
- **Passage-based processing:** Split documents into paragraph-based chunks (separated by blank lines) while retaining their original line positions.
- **Phrase search:** Find passages containing a query phrase, with case-insensitive matching and punctuation normalisation.
- **Relevance ranking:** Rank documents and passages using a custom scoring system based on match counts, and rank question-answering results using keyword matches weighted by inverse document frequency (IDF).
- **AI-assisted question answering:** Use Google's Gemini API to generate answers from the five highest-ranked passages.
- **Source references:** Return source filenames, document IDs, chunk numbers and line positions alongside generated answers.
- **Grounded responses:** Instruct the LLM to use only the retrieved information, avoid unsupported claims and state when the available information is insufficient.

### Frontend

- **Document library:** View uploaded documents with their word counts.
- **Upload:** Upload `.txt` files with loading, success and error feedback; the list refreshes automatically.
- **Document viewer:** Select a document to read its full content.
- **Search:** Search across all documents and view matching passages grouped by document, with line ranges.
- **Ask AI:** Ask a question and receive a generated answer with a list of its sources.
- **Error handling:** Loading and error states for every request, the server’s own error messages (such as invalid uploads or missing documents), and a clear message when the backend is unreachable.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | REST API development |
| SQLAlchemy | ORM and database operations |
| SQLite | Persistent document storage |
| Uvicorn | ASGI server |
| Google Gemini API / Gen AI SDK | AI-assisted answer generation |
| python-dotenv | Environment variable management |
| React | Frontend user interface |
| TypeScript | Typed frontend code |
| Vite | Frontend build tool and development server |

## Project Structure

```text
knowledgebase/
├── main.py              # API endpoints and retrieval logic
├── models.py            # SQLAlchemy database models
├── database.py          # Database engine, sessions and initialisation
├── ai_service.py        # Gemini API integration and answer generation
├── requirements.txt     # Python dependencies
├── .env                 # API credentials and configuration (not committed)
├── knowledgebase.db     # SQLite database (created at runtime)
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx     # Application entry point
        ├── App.tsx      # Main UI: documents, search and Ask AI sections
        ├── api.ts       # Functions for calling the backend API
        ├── types.ts     # TypeScript interfaces for API responses
        ├── App.css      # Component styles
        └── index.css    # Global styles
```

The SQLite database, virtual environment and `.env` file are local runtime files and should not be committed. In particular, `.env` contains the Gemini API key and must remain private.

## Getting Started

### Prerequisites

- Python 3.11 or later and pip
- Node.js and npm
- A Google AI Studio API key

### 1. Clone the repository

```bash
git clone https://github.com/ArashHafiz/knowledgebase
cd knowledgebase
```

### 2. Set up the backend

Create and activate a virtual environment.

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

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace `your_api_key_here` with your Google AI Studio API key. The model can be changed through `GEMINI_MODEL`; if it is not set, the application defaults to `gemini-3.5-flash-lite`.

Start the API server:

```bash
python -m uvicorn main:app --reload
```

- **API base URL:** http://127.0.0.1:8000
- **Interactive API documentation (Swagger):** http://127.0.0.1:8000/docs

The database and `documents` table are created automatically on startup.

### 3. Set up the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Use `localhost` rather than `127.0.0.1`: the backend's CORS configuration only allows the `http://localhost:5173` origin.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/documents` | List documents and their metadata |
| `GET` | `/documents/{doc_id}` | Retrieve a document by its ID |
| `GET` | `/search?query={phrase}` | Search document contents and retrieve matching passages |
| `POST` | `/ask?question={question}` | Retrieve relevant passages and generate an AI-assisted answer |
| `POST` | `/upload` | Upload and store a text document |

### API Errors

| Status | Meaning |
|---|---|
| `400` | Uploaded file is not valid UTF-8 text |
| `404` | Document not found |
| `502` | Gemini service failed to generate an answer |

### Upload a document

`POST /upload` accepts a UTF-8 `.txt` file as multipart form data, with the file field named `file`. The API stores the filename, full text, word count and creation timestamp. Each document receives a unique database ID, so multiple documents can share a filename.

### Search documents

```text
/search?query=uranium
```

1. Normalises the query: lowercases it and removes punctuation, including possessive apostrophes.
2. Splits each stored document into paragraph-based chunks.
3. Selects chunks that contain the **whole normalised query phrase**.
4. Scores each matching document from its matching chunks and matching words, adjusted for document length.
5. Returns matching documents ranked by score, with passages ranked within each document.

The response includes document IDs, filenames, chunk numbers, original line positions, match counts and scores. Search uses keyword and substring matching rather than semantic similarity.

### Ask a question

```text
/ask?question=Where%20is%20uranium%20found
```

1. **Question processing:** Normalises the question and removes common stop words to extract keywords.
2. **Passage retrieval:** Searches the documents for each keyword individually.
3. **Relevance ranking:** Weights each keyword by inverse document frequency (IDF), so keywords found in fewer documents count for more.
4. **Passage selection:** Combines the matches, ranks the passages and selects the five highest-ranked.
5. **Answer generation:** Passes the original question and selected passages to the Gemini API.
6. **Source attribution:** Returns the answer alongside structured references to the passages used.

If retrieval finds no passages, the API returns a fixed "insufficient information" message without calling Gemini. If the Gemini call fails, the API returns a `502` error. The LLM is instructed to answer only from the retrieved passages, cite them and acknowledge insufficient evidence.

The response contains:

- `answer`: the generated natural-language answer.
- `sources`: references with filenames, document IDs, chunk numbers and line positions.

The retrieval pipeline and the LLM integration are kept separate, so retrieval can be evaluated and improved independently of the language model.

## Database Design

The `Document` model maps to the SQLite `documents` table.

| Field | Description |
|---|---|
| `id` | Auto-incrementing primary key |
| `filename` | Original filename |
| `content` | Full text content |
| `date_added` | Record creation timestamp |
| `word_count` | Number of whitespace-separated tokens |

## Current Limitations

- Only UTF-8 text content is supported. PDFs and other formats are not.
- `/search` matches whole phrases only, so a query of non-adjacent words returns nothing. `/ask` avoids this by searching keyword by keyword, but treats multi-word terms such as "United States" as separate keywords.
- Retrieval uses keyword matching rather than semantic similarity or embeddings, and relevance scores are heuristic rather than calibrated.
- Retrieval reads every document on each request, which will not scale to large collections.
- Question answering uses a fixed maximum of five passages, which may not always provide enough context.
- AI-generated answers depend on retrieval quality and may still contain unsupported claims or inaccurate citations.
- Upload validation is limited to UTF-8 decoding. There are no file-type or file-size limits yet, and automated test coverage is still being developed.
- The frontend is functional but minimally styled.
- The application uses a local SQLite database with no migration framework.

## Future Development

- Evaluate retrieval quality against a representative question set (factual, descriptive, multi-part, multi-hop, ambiguous and unsupported questions), and improve ranking and filtering based on the results.
- Add key-phrase matching and improved relevance scoring.
- Optimise retrieval for larger collections.
- Add automated tests for endpoints, database operations, retrieval and AI integration.
- Improve input validation, error handling and database management.
- Support additional document formats and more robust text extraction.
- Polish the frontend design.

## Motivation

This project explores document ingestion, relational data modelling, REST API design, information retrieval, LLM integration and full-stack development with React and TypeScript.

Its central objective is a retrieval pipeline that identifies relevant information in a personal knowledge base before passing selected passages to an LLM. Rather than supplying entire documents indiscriminately, the system retrieves a limited amount of relevant context, using model tokens efficiently and providing a basis for source-grounded answers.

The longer-term goal is a practical knowledge management application that combines structured document storage, effective information retrieval and AI-assisted access to personal collections of information.
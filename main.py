from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from models import Document
from database import init_db, get_db
from ai_service import generate_answer
import re
import math

app = FastAPI()
init_db()

STOP_WORDS = ["the", "is", "in", "and", "to", "of", "a", "that", "it", 
			   "on", "for", "with", "as", "this", "by", "an", "be", "are", "from", "at",
			   "or", "which", "who", "but", "have", "has", "was", "were", "they",
			   "their", "them", "he", "she", "his", "her", "when", "where", "what", 
			   "how", "why", "if", "then", "else", "all", "any", "some", "yes", 
			   "do", "does", "did",]

def normalise_text(text):
	text = text.lower()
	text = re.sub(r"'s\b", "", text) # Remove possessive apostrophes
	text = re.sub(r"[^\w\s]", "", text) # Remove punctuation
	return text.split()

def split_into_chunks(content):
    content = content.replace("\r\n", "\n").replace("\r", "\n") # Make line breaks consistent (standardise to Unix-style)
    chunks = []

    paragraphs = re.finditer(
        r"\S.*?(?=\n[ \t]*\n|\Z)",
        content,
        re.DOTALL
    ) # Find paragraphs separated by one or more blank lines

    for chunk_number, match in enumerate(paragraphs, start=1):
        chunk_text = match.group().strip() # Remove leading/trailing whitespace

        if not chunk_text:
            continue

		# Number the lines
        start_line = content.count("\n", 0, match.start()) + 1
        end_line = content.count("\n", 0, match.end()) + 1

        chunks.append({
            "chunk_number": chunk_number,
            "start_line": start_line,
            "end_line": end_line,
            "text": chunk_text
        })

    return chunks

# list doc
@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
	docs = db.query(Document).all()

	return [
		{
			"id": d.id,
			"filename": d.filename,
			"word_count": d.word_count
		} for d in docs
	]

# get doc
@app.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
	doc = db.query(Document).filter(Document.id == doc_id).first()

	if not doc:
		return {"error": "Document not found"}
	
	return {
		"id": doc.id,
		"filename": doc.filename,
		"content": doc.content,
		"word_count": doc.word_count,
	}

# search
@app.get("/search")
def search(query: str, db: Session = Depends(get_db)):
    query_words = normalise_text(query)

    if not query_words:
        return {"total_score": 0, "results": []} # Return empty results for nothingburgers

    normalised_query = " ".join(query_words)
    docs = db.query(Document).all()
    results = []
    total_score = 0

    for d in docs:
        chunks = split_into_chunks(d.content)
        doc_results = []
        doc_matching_words = 0
        doc_matching_chunks = 0

        for chunk in chunks:
            normalised_chunk = normalise_text(chunk["text"])
            normalised_chunk_text = " ".join(normalised_chunk)

            if normalised_query in normalised_chunk_text:
                matching_words = sum(
                    1 for word in normalised_chunk
                    if any(query_word in word for query_word in query_words)
                )

                doc_matching_chunks += 1
                doc_matching_words += matching_words

                doc_results.append({
                    "chunk_number": chunk["chunk_number"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "doc_id": d.id,
                    "filename": d.filename,
                    "text": chunk["text"],
                    "matches": matching_words
                })

        if doc_results:
            doc_score = (
                doc_matching_chunks * 3 + doc_matching_words * 2
            ) / max(1, d.word_count)

            total_score += doc_score

            doc_results = sort_document_results(doc_results)

            results.append({
                "id": d.id,
                "filename": d.filename,
                "results": doc_results,
                "score": doc_score
            })

    results = sort_search_results(results)

    return {"total_score": total_score, "results": results}

# sort results in descending order of score
def sort_search_results(results):
	return sorted(results, key=lambda x: x["score"], reverse=True)

def sort_document_results(results):
	return sorted(results, key=lambda x: x["matches"], reverse=True)

# ask questions
@app.post("/ask")
def ask_question(question: str, db: Session = Depends(get_db)):
    words = normalise_text(question)
    keywords = [word for word in words if word not in STOP_WORDS]

    results = {}
    total_documents = db.query(Document).count()

    for keyword in keywords:
        search_result = search(keyword, db)

        document_frequency = len(search_result["results"])

        idf = math.log(
            (total_documents + 1) / (document_frequency + 1)
        ) + 1

        for document in search_result["results"]:
            for chunk_result in document["results"]:

                results_key = (
                    f"{chunk_result['doc_id']}_"
                    f"{chunk_result['chunk_number']}"
                )

                if results_key not in results:
                    results[results_key] = {
                        "doc_id": chunk_result["doc_id"],
                        "filename": chunk_result["filename"],
                        "chunk_number": chunk_result["chunk_number"],
                        "start_line": chunk_result["start_line"],
                        "end_line": chunk_result["end_line"],
                        "text": chunk_result["text"],
                        "matched_keywords": set(),
                        "score": 0
                    }

                if keyword not in results[results_key]["matched_keywords"]:
                    results[results_key]["matched_keywords"].add(keyword)
                    results[results_key]["score"] += idf

    ranked_results = [{
        **result,
        "matched_keywords": sorted(result["matched_keywords"])
    } for result in results.values()]

    ranked_results = sorted(
        ranked_results,
        key=lambda x: (x["score"], len(x["matched_keywords"])),
        reverse=True
    )

    retrieved_chunks = ranked_results[:5]

    if not retrieved_chunks:
        return {
            "answer": "The available documents do not contain sufficient information to answer this question.",
            "sources": []
        }

    try:
        answer = generate_answer(question, retrieved_chunks)

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail="The AI service could not generate an answer. Please try again later."
        ) from e

    sources = [
        {
            "filename": chunk["filename"],
            "doc_id": chunk["doc_id"],
            "chunk_number": chunk["chunk_number"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"]
        }
        for chunk in retrieved_chunks
    ]

    return {
        "answer": answer,
        "sources": sources
    }

# sort question results in descending order of score
def sort_question_results(results):
	return sorted(results, key=lambda x: x["total_score"], reverse=True)

# upload
@app.post("/upload")
async def upload_file(
	file: UploadFile = File(...),
	db: Session = Depends(get_db)
):
	content = await file.read()
	text = content.decode("utf-8")
	doc = Document(filename=file.filename, content=text, word_count=len(text.split()))

	db.add(doc)
	db.commit()
	db.refresh(doc)

	return {
		"id": doc.id,
		"filename": doc.filename,
		"word_count": doc.word_count
	}
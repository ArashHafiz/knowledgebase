from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from models import Document
from database import init_db, get_db
import re

app = FastAPI()
init_db()

STOP_WORDS = ["the", "is", "in", "and", "to", "of", "a", "that", "it", 
			   "on", "for", "with", "as", "this", "by", "an", "be", "are", "from", "at",
			   "or", "which", "who", "but", "not", "have", "has", "was", "were", "they",
			   "their", "them", "he", "she", "his", "her", "when", "where", "what", 
			   "how", "why", "if", "then", "else", "all", "any", "some", "no", "yes", 
			   "do", "does", "did",]

def normalise_text(text):
	text = text.lower()
	text = re.sub(r"'s\b", "", text) # Remove possessive apostrophes
	text = re.sub(r"[^\w\s]", "", text) # Remove punctuation
	return text.split()

# list doc
@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
	docs = db.query(Document).all()

	return [
		{
			"id": d.id,
			"filename": d.filename,
			"word_count": d.word_count,
			"line_count": d.line_count
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
		"line_count": doc.line_count
	}

# search
@app.get("/search")
def search(query: str, db: Session = Depends(get_db)):
    query_words = normalise_text(query)

    if not query_words: # Return empty results if query is empty or only has stop words (nothingburger)
        return {"total_score": 0, "results": []}

    normalised_query = " ".join(query_words)
    docs = db.query(Document).all()
    results = []
    total_score = 0

    for d in docs:
        normalised_content = " ".join(normalise_text(d.content))

        if normalised_query in normalised_content:
            doc_results = []
            doc_matching_words = 0
            doc_matching_lines = 0

            for line_number, line in enumerate(d.content.splitlines(), start=1):
                normalised_line = " ".join(normalise_text(line))

                if normalised_query in normalised_line:
                    matching_words = sum(
                        1 for word in normalise_text(line)
                        if any(query_word in word for query_word in query_words)
                    )

                    doc_matching_lines += 1
                    doc_matching_words += matching_words

                    doc_results.append({
                        "line_number": line_number,
                        "doc_id": d.id,
                        "filename": d.filename,
                        "line": line.strip(),
                        "matches": matching_words
                    })

            doc_results = sort_document_results(doc_results)

            doc_score = (
                doc_matching_lines * 3 + doc_matching_words * 2
            ) / max(1, d.word_count)

            total_score += doc_score

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
	
	for keyword in keywords:
		search_result = search(keyword, db)
		for document in search_result["results"]:
			for line_result in document["results"]:
				results_key = f"{line_result['doc_id']}_{line_result['line_number']}" # Makes string in form X_N. Note JSON obj keys must be string

				if results_key not in results: # Avoid duplicate results
					results[results_key] = {
						"doc_id": line_result["doc_id"],
						"filename": line_result["filename"],
						"line_number": line_result["line_number"],
						"line": line_result["line"],
						"matched_keywords": set() # Make set to avoid duplicates
					}
					
				results[results_key]["matched_keywords"].add(keyword)

	for result in results.values():
		result["score"] = len(result["matched_keywords"]) # Score is number of matched keywords

	ranked_results = [{
		**result, # Unpack the result dictionary
		"matched_keywords": sorted(result["matched_keywords"]) # Overwrite matched_keywords; convert set to sorted list
	} for result in results.values()]

	ranked_results = sorted(ranked_results, key = lambda x: x["score"], reverse = True) # Sort results in descending order of score
	return ranked_results[:5] # Top 5

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
	doc = Document(filename=file.filename, content=text, word_count=len(text.split()), line_count=len(text.splitlines()))

	db.add(doc)
	db.commit()
	db.refresh(doc)

	return {
		"id": doc.id,
		"filename": doc.filename,
		"word_count": doc.word_count,
		"line_count": doc.line_count
	}
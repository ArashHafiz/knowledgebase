from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from models import Document
from database import init_db, get_db
import string

app = FastAPI()
init_db()

STOP_WORDS = ["the", "is", "in", "and", "to", "of", "a", "that", "it", 
			   "on", "for", "with", "as", "this", "by", "an", "be", "are", "from", "at",
			   "or", "which", "but", "not", "have", "has", "was", "were", "they",
			   "their", "them", "he", "she", "his", "her", "when", "where", "what", 
			   "how", "why", "if", "then", "else", "all", "any", "some", "no", "yes", 
			   "do", "does", "did",]

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
	docs = db.query(Document).all()
	results = []
	total_score = 0
	
	for d in docs:
		if query.lower() in d.content.lower():
			doc_results = []
			doc_matching_words = 0
			doc_matching_lines = 0
			doc_score = 0

			for line in d.content.splitlines():
				if query.lower() in line.lower():
					matching_words = 0
					doc_matching_lines += 1
					for word in line.split():
						if query.lower() in word.lower():
							matching_words += 1
					doc_matching_words += matching_words

					doc_results.append({
						"id": d.id,
						"filename": d.filename,
						"line": line.strip(),
						"matches": matching_words
					})

			doc_results = sort_document_results(doc_results)
			doc_score = (doc_matching_lines * 3 + doc_matching_words * 2)/max(1, d.word_count)
			total_score += doc_score
			
			results.append({
				"id": d.id,
				"filename": d.filename,
				"results": doc_results,
				"score": doc_score
			})

	results = sort_search_results(results)

	return {
		"total_score": total_score,
		"results": results
	}

# sort results in descending order of score
def sort_search_results(results):
	return sorted(results, key=lambda x: x["score"], reverse=True)

def sort_document_results(results):
	return sorted(results, key=lambda x: x["matches"], reverse=True)

# ask questions
@app.post("/ask")
def ask_question(question: str, db: Session = Depends(get_db)):
	words = question.lower().split()
	words = words.translate(str.maketrans("", "", string.punctuation))
	keywords = [word for word in words if word not in STOP_WORDS]
	results = []
	
	for keyword in keywords:
		result = search(keyword, db)
		if result["total_score"] > 0:
			results.append(result)

	return results

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
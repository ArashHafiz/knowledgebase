import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=API_KEY)

def generate_answer(question, retrieved_chunks):
    context = ""

    for chunk in retrieved_chunks:
        context += (
            f"\nSource: {chunk['filename']}\n"
            f"Documents: {chunk['doc_id']}\n"
            f"Chunk: {chunk['chunk_number']}\n"
            f"Text: {chunk['text']}\n"
        )
    prompt = f"""
You are an AI assistant for a personal knowledge base.

Answer the user's question using only the information provided
in the retrieved source passages.

Instructions:
- Answer using only the information provided in the retrieved passages.
- Do not introduce unsupported facts, assumptions, or external knowledge.
- Distinguish explicitly stated information from reasonable inferences.
- If combining multiple passages, ensure that they collectively support
  the conclusion.
- If the passages do not contain sufficient information, explicitly
  state that the available information is insufficient.
- Do not treat keyword overlap alone as evidence that a passage
  answers the question.
- Write a clear, direct and appropriately detailed answer.
- Cite the specific source filename and chunk number supporting
  each relevant claim.
- Do not invent or modify source references.

Retrieved passages:
{context}

User question:
{question}
        """
    response = client.models.generate_content(
            model=MODEL,
            contents=prompt
    )
    return response.text
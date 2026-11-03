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
        - Do not introduce facts that are not supported by the passages.
        - If the passages do not contain enough information to answer,
        explicitly state that the available information is insufficient.
        - Write a clear, direct answer.
        - Cite the source filename and chunk number for the information
        used in your answer.
        - If multiple passages support the answer, cite all relevant sources.

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
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found.")

print(f"Using model: {model}")

client = genai.Client(api_key=api_key)

print("Sending request to Gemini...")

interaction = client.models.generate_content(
    model=model, 
    contents="Hello! This is a test prompt.",
)

print("Response received.")
print(interaction.text)
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
        You are a document assistant.
    
        Answer ONLY using the provided context.
    
        After answering, return the source filenames that were actually used.
    
        Return valid JSON only.
    
        Context:
        {context}
    
        Question:
        {question}
    
        Format:
        {{
          "question": "user question",
          "answer": "...",
          "sources": ["file1.pdf"]
        }}
        """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

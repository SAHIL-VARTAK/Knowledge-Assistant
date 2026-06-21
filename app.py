import json

from fastapi import FastAPI, UploadFile, File
import shutil
import os

from services.chunker import chunk_text
from services.document_loader import load_pdf
from services.vector_store import save_chunks, search_documents, get_sources, clear_collection
from services.rag import generate_answer
from utils.ai_response_cleaner import clean_ai_response

app = FastAPI()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = load_pdf(file_path)

    chunks = chunk_text(extracted_text)

    save_chunks(chunks, file.filename)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "characters_extracted": len(extracted_text),
        "chunks_created": len(chunks)
    }


@app.get("/search")
def search(query: str):
    results = search_documents(query)

    return {
        "query": query,
        "documents": results["documents"][0]
    }


@app.get("/ask")
def ask(question: str):
    results = search_documents(question)
    documents = results.get("documents", [])

    if not documents or not documents[0]:
        return {
            "answer": "No relevant information found."
        }

    context_parts = []
    for doc, metadata in zip(
            results["documents"][0],
            results["metadatas"][0]
    ):
        context_parts.append(
            f"""
            Source: {metadata['source']}
        
            Content:
            {doc}
            """
        )

    context = "\n\n".join(context_parts)

    response_text = generate_answer(
        question=question,
        context=context
    )

    response_text = clean_ai_response(response_text)

    try:
        response_json = json.loads(response_text)

        return {
            "question": response_json.get("question"),
            "answer": response_json.get("answer"),
            "sources": response_json.get("sources", [])
        }
    except Exception:
        return {
            "question": question,
            "answer": f"Error with Gemini API: {response_text}",
            "sources": []
        }


@app.get("/sources")
def sources():
    return {
        "sources": get_sources()
    }


@app.post("/clear")
def clear():
    clear_collection()

    return {
        "message": "Knowledge base cleared successfully."
    }


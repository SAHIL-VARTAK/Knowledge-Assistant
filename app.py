import os
import shutil

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from config.model_registry import CURRENT_CONFIG, MODEL_REGISTRY
from services.chat_memory import add_message, clear_history, get_history
from services.chunker import chunk_text
from services.document_loader import load_document
from services.rag import generate_answer
from services.vector_store import (
    clear_collection,
    get_sources,
    save_chunks,
    search_documents,
)
from utils.ai_response_cleaner import parse_ai_response
from utils.file_cleanup import clear_application_data

app = FastAPI()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


class ModelConfig(BaseModel):
    provider: str
    model: str
    api_key: str


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):  # noqa: B008
    # Skip ruff check since this is Fast API pattern
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = load_document(file_path)

    except ValueError as e:
        os.remove(file_path)
        return {"message": str(e)}

    chunks = chunk_text(extracted_text)

    save_chunks(chunks, file.filename)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "characters_extracted": len(extracted_text),
        "chunks_created": len(chunks),
    }


@app.get("/search")
def search(query: str):
    results = search_documents(query)

    return {"query": query, "documents": results["documents"][0]}


@app.get("/ask")
def ask(question: str):
    results = search_documents(question)
    documents = results.get("documents", [])

    if not documents or not documents[0]:
        return {"answer": "No relevant information found."}

    context_parts = []
    for doc, metadata in zip(results["documents"][0], results["metadatas"][0], strict=True):
        context_parts.append(
            f"""
            Source: {metadata["source"]}
        
            Content:
            {doc}
            """
        )

    context = "\n\n".join(context_parts)

    history = get_history()
    history_text = ""

    for message in history:
        history_sources = ", ".join(message.get("source", []))
        history_text += (
            f"Role: {message.get('role', '')}\nContent: {message.get('content', '')}\nSources: {history_sources}\n\n"
        )

    response_text = generate_answer(question=question, context=context, history=history_text)

    try:
        response_data = parse_ai_response(response_text, question)

        add_message("user", question, None)
        add_message("assistant", response_data.get("answer"), response_data.get("sources", None))

        return {
            "question": response_data.get("question"),
            "answer": response_data.get("answer"),
            "sources": response_data.get("sources", []),
        }
    except Exception:
        return {"question": question, "answer": f"Error with Gemini API: {response_text}", "sources": []}


@app.get("/sources")
def sources():
    return {"sources": get_sources()}


@app.post("/clear")
def clear():
    clear_collection()
    clear_history()
    clear_application_data()

    return {"message": "Knowledge base cleared successfully."}


@app.post("/clear-chat")
def clear_chat():
    clear_history()

    return {"message": "Chat history cleared."}


@app.get("/providers")
def get_providers():
    return MODEL_REGISTRY


@app.post("/model-config")
def update_model_config(config: ModelConfig):
    CURRENT_CONFIG["provider"] = config.provider
    CURRENT_CONFIG["model"] = config.model
    CURRENT_CONFIG["api_key"] = config.api_key or os.getenv("GEMINI_API_KEY")

    return {"message": "Configuration updated."}

from fastapi import FastAPI, UploadFile, File
import shutil
import os

from services.chunker import chunk_text
from services.document_loader import load_pdf

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
    print(len(chunks))

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "characters_extracted": len(extracted_text)
    }

from pathlib import Path

from docx import Document
from pypdf import PdfReader

SUPPORTED_CODE_FILES = [".py", ".java", ".js", ".ts", ".html", ".css", ".sql", ".cpp", ".c", ".cs"]


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text)


def load_docx(file_path: str) -> str:
    document = Document(file_path)
    text = []

    for paragraph in document.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)


def load_text(file_path: str) -> str:
    with open(file_path, encoding="utf-8") as file:
        return file.read()


def load_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    elif extension == ".docx":
        return load_docx(file_path)

    elif extension in [".txt", ".md"]:
        return load_text(file_path)

    elif extension in SUPPORTED_CODE_FILES:
        return load_text(file_path)

    raise ValueError(f"Unsupported file type: {extension}")

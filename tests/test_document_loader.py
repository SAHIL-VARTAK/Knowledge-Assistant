from unittest.mock import MagicMock, patch

import pytest

from services.document_loader import (
    SUPPORTED_CODE_FILES,
    load_document,
    load_docx,
    load_pdf,
    load_text,
)


# ---------- load_pdf ----------
@patch("services.document_loader.PdfReader")
def test_load_pdf(mock_pdf_reader):
    page1 = MagicMock()
    page1.extract_text.return_value = "Page One"

    page2 = MagicMock()
    page2.extract_text.return_value = "Page Two"

    mock_pdf_reader.return_value.pages = [page1, page2]

    result = load_pdf("resume.pdf")

    assert result == "Page One\nPage Two"


@patch("services.document_loader.PdfReader")
def test_load_pdf_ignores_empty_pages(mock_pdf_reader):
    page1 = MagicMock()
    page1.extract_text.return_value = "Page One"

    page2 = MagicMock()
    page2.extract_text.return_value = None

    mock_pdf_reader.return_value.pages = [page1, page2]

    result = load_pdf("resume.pdf")

    assert result == "Page One"


# ---------- load_docx ----------
@patch("services.document_loader.Document")
def test_load_docx(mock_document):
    paragraph1 = MagicMock(text="First")
    paragraph2 = MagicMock(text="Second")

    mock_document.return_value.paragraphs = [
        paragraph1,
        paragraph2,
    ]

    result = load_docx("resume.docx")

    assert result == "First\nSecond"


# ---------- load_text ----------
def test_load_text(tmp_path):
    file = tmp_path / "sample.txt"

    file.write_text("Hello World", encoding="utf-8")

    assert load_text(str(file)) == "Hello World"


# ---------- load_document routing ----------
@patch("services.document_loader.load_pdf")
def test_load_document_pdf(mock_load_pdf):
    mock_load_pdf.return_value = "PDF"

    assert load_document("resume.pdf") == "PDF"

    mock_load_pdf.assert_called_once_with("resume.pdf")


@patch("services.document_loader.load_docx")
def test_load_document_docx(mock_load_docx):
    mock_load_docx.return_value = "DOCX"

    assert load_document("resume.docx") == "DOCX"

    mock_load_docx.assert_called_once_with("resume.docx")


@patch("services.document_loader.load_text")
def test_load_document_text(mock_load_text):
    mock_load_text.return_value = "TEXT"

    assert load_document("notes.txt") == "TEXT"

    mock_load_text.assert_called_once_with("notes.txt")


@patch("services.document_loader.load_text")
def test_load_document_markdown(mock_load_text):
    mock_load_text.return_value = "MARKDOWN"

    assert load_document("README.md") == "MARKDOWN"


@pytest.mark.parametrize("extension", SUPPORTED_CODE_FILES)
@patch("services.document_loader.load_text")
def test_load_document_code_files(
    mock_load_text,
    extension,
):
    mock_load_text.return_value = "CODE"

    filename = f"test{extension}"

    assert load_document(filename) == "CODE"

    mock_load_text.assert_called_once_with(filename)


def test_load_document_unsupported():
    with pytest.raises(ValueError) as exception:
        load_document("image.png")

    assert "Unsupported file type" in str(exception.value)

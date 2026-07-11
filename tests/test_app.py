from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from config.model_registry import CURRENT_CONFIG

client = TestClient(app)


def test_health():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "running"}


@patch("app.load_document")
@patch("app.chunk_text")
@patch("app.save_chunks")
def test_upload_success(
    mock_save_chunks,
    mock_chunk_text,
    mock_load_document,
):
    mock_load_document.return_value = "Hello World"

    mock_chunk_text.return_value = [
        "chunk1",
        "chunk2",
    ]

    response = client.post(
        "/upload",
        files={
            "file": (
                "resume.txt",
                b"hello world",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "File uploaded successfully"
    assert data["filename"] == "resume.txt"
    assert data["characters_extracted"] == 11
    assert data["chunks_created"] == 2

    mock_save_chunks.assert_called_once()


@patch("app.os.remove")
@patch("app.load_document")
def test_upload_invalid_file(
    mock_load_document,
    mock_remove,
):
    mock_load_document.side_effect = ValueError("Unsupported file type")

    response = client.post(
        "/upload",
        files={
            "file": (
                "image.png",
                b"abc",
                "image/png",
            )
        },
    )

    assert response.status_code == 200

    assert response.json() == {"message": "Unsupported file type"}

    mock_remove.assert_called_once()


@patch("app.search_documents")
def test_search(mock_search):
    mock_search.return_value = {"documents": [["doc1", "doc2"]]}

    response = client.get(
        "/search",
        params={"query": "resume"},
    )

    assert response.status_code == 200

    assert response.json() == {
        "query": "resume",
        "documents": [
            "doc1",
            "doc2",
        ],
    }


@patch("app.search_documents")
def test_ask_no_documents(mock_search):
    mock_search.return_value = {
        "documents": [],
    }

    response = client.get(
        "/ask",
        params={"question": "Hello"},
    )

    assert response.status_code == 200

    assert response.json() == {"answer": "No relevant information found."}


@patch("app.add_message")
@patch("app.parse_ai_response")
@patch("app.generate_answer")
@patch("app.get_history")
@patch("app.search_documents")
def test_ask_success(
    mock_search,
    mock_history,
    mock_generate,
    mock_parser,
    mock_add_message,
):
    mock_search.return_value = {
        "documents": [["My name is Sahil"]],
        "metadatas": [[{"source": "resume.pdf"}]],
    }

    mock_history.return_value = []

    mock_generate.return_value = "RAW RESPONSE"

    mock_parser.return_value = {
        "question": "What is my name?",
        "answer": "Sahil",
        "sources": ["resume.pdf"],
    }

    response = client.get(
        "/ask",
        params={"question": "What is my name?"},
    )

    assert response.status_code == 200

    assert response.json() == {
        "question": "What is my name?",
        "answer": "Sahil",
        "sources": ["resume.pdf"],
    }

    assert mock_add_message.call_count == 2


@patch("app.parse_ai_response")
@patch("app.generate_answer")
@patch("app.get_history")
@patch("app.search_documents")
def test_ask_parser_exception(
    mock_search,
    mock_history,
    mock_generate,
    mock_parser,
):
    mock_search.return_value = {
        "documents": [["content"]],
        "metadatas": [[{"source": "resume.pdf"}]],
    }

    mock_history.return_value = []

    mock_generate.return_value = "RAW RESPONSE"

    mock_parser.side_effect = Exception("Parser failed")

    response = client.get(
        "/ask",
        params={"question": "Hello"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "Hello"
    assert "Error with Gemini API" in data["answer"]
    assert data["sources"] == []


@patch("app.get_sources")
def test_sources(mock_sources):
    mock_sources.return_value = [
        "resume.pdf",
        "notes.pdf",
    ]

    response = client.get("/sources")

    assert response.status_code == 200

    assert response.json() == {
        "sources": [
            "resume.pdf",
            "notes.pdf",
        ]
    }


@patch("app.clear_application_data")
@patch("app.clear_history")
@patch("app.clear_collection")
def test_clear(
    mock_clear_collection,
    mock_clear_history,
    mock_clear_application_data,
):
    response = client.post("/clear")

    assert response.status_code == 200

    assert response.json() == {"message": "Knowledge base cleared successfully."}

    mock_clear_collection.assert_called_once()
    mock_clear_history.assert_called_once()
    mock_clear_application_data.assert_called_once()


@patch("app.clear_history")
def test_clear_chat(mock_clear_history):
    response = client.post("/clear-chat")

    assert response.status_code == 200

    assert response.json() == {"message": "Chat history cleared."}

    mock_clear_history.assert_called_once()


def test_get_providers():
    response = client.get("/providers")

    assert response.status_code == 200

    data = response.json()

    assert "Gemini" in data
    assert "Ollama" in data


def test_update_model_config():
    response = client.post(
        "/model-config",
        json={
            "provider": "Gemini",
            "model": "gemini-2.5-pro",
            "api_key": "test-key",
        },
    )

    assert response.status_code == 200

    assert response.json() == {"message": "Configuration updated."}

    assert CURRENT_CONFIG["provider"] == "Gemini"
    assert CURRENT_CONFIG["model"] == "gemini-2.5-pro"
    assert CURRENT_CONFIG["api_key"] == "test-key"


def test_update_model_config_env_fallback(monkeypatch):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "env-key",
    )

    response = client.post(
        "/model-config",
        json={
            "provider": "Gemini",
            "model": "gemini-2.5-flash",
            "api_key": "",
        },
    )

    assert response.status_code == 200

    assert CURRENT_CONFIG["api_key"] == "env-key"


@patch("app.add_message")
@patch("app.parse_ai_response")
@patch("app.generate_answer")
@patch("app.get_history")
@patch("app.search_documents")
def test_ask_with_chat_history(
    mock_search,
    mock_history,
    mock_generate,
    mock_parser,
    mock_add_message,
):
    mock_search.return_value = {
        "documents": [["Python is a programming language."]],
        "metadatas": [[{"source": "python.pdf"}]],
    }

    mock_history.return_value = [
        {
            "role": "user",
            "content": "What is Python?",
            "source": [],
        },
        {
            "role": "assistant",
            "content": "Python is a programming language.",
            "source": ["python.pdf"],
        },
    ]

    mock_generate.return_value = "RAW RESPONSE"

    mock_parser.return_value = {
        "question": "Tell me more",
        "answer": "Python is widely used.",
        "sources": ["python.pdf"],
    }

    response = client.get(
        "/ask",
        params={
            "question": "Tell me more",
        },
    )

    assert response.status_code == 200

    # Verify history formatting passed to generate_answer()
    kwargs = mock_generate.call_args.kwargs

    assert kwargs["question"] == "Tell me more"

    assert "Role: user\nContent: What is Python?\nSources: \n\n" in kwargs["history"]

    assert "Role: assistant\nContent: Python is a programming language.\nSources: python.pdf\n\n" in kwargs["history"]

    assert "Source: python.pdf" in kwargs["context"]
    assert "Python is a programming language." in kwargs["context"]

    assert mock_add_message.call_count == 2

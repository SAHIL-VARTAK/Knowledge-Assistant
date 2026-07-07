from unittest.mock import MagicMock, patch

from config.model_registry import CURRENT_CONFIG
from services.rag import generate_answer


@patch("services.rag.get_prompt")
def test_gemini_missing_api_key(mock_prompt):
    CURRENT_CONFIG["provider"] = "Gemini"
    CURRENT_CONFIG["model"] = "gemini-2.5-flash"
    CURRENT_CONFIG["api_key"] = ""

    mock_prompt.return_value = "PROMPT"

    result = generate_answer(
        question="Hello",
        context="Context",
        history="History",
    )

    assert "Gemini API key is not configured" in result


@patch("services.rag.genai.Client")
@patch("services.rag.get_prompt")
def test_gemini_success(
    mock_prompt,
    mock_client,
):
    CURRENT_CONFIG["provider"] = "Gemini"
    CURRENT_CONFIG["model"] = "gemini-2.5-flash"
    CURRENT_CONFIG["api_key"] = "abc"

    mock_prompt.return_value = "PROMPT"

    response = MagicMock()
    response.text = "ANSWER"

    client = MagicMock()
    client.models.generate_content.return_value = response

    mock_client.return_value = client

    result = generate_answer(
        "Question",
        "Context",
        "History",
    )

    assert result == "ANSWER"


@patch("services.rag.genai.Client")
@patch("services.rag.get_prompt")
def test_gemini_exception(
    mock_prompt,
    mock_client,
):
    CURRENT_CONFIG["provider"] = "Gemini"
    CURRENT_CONFIG["model"] = "gemini-2.5-flash"
    CURRENT_CONFIG["api_key"] = "abc"

    mock_prompt.return_value = "PROMPT"

    client = MagicMock()

    client.models.generate_content.side_effect = Exception("Quota exceeded")

    mock_client.return_value = client

    result = generate_answer(
        "Question",
        "Context",
        "History",
    )

    assert "Failed to generate a response using Gemini" in result


@patch("services.rag.ollama.chat")
@patch("services.rag.get_prompt")
def test_ollama_success(
    mock_prompt,
    mock_chat,
):
    CURRENT_CONFIG["provider"] = "Ollama"
    CURRENT_CONFIG["model"] = "phi4-mini"

    mock_prompt.return_value = "PROMPT"

    mock_chat.return_value = {
        "message": {
            "content": "OLLAMA ANSWER",
        }
    }

    result = generate_answer(
        "Question",
        "Context",
        "History",
    )

    assert result == "OLLAMA ANSWER"


@patch("services.rag.get_prompt")
def test_invalid_provider(mock_prompt):
    CURRENT_CONFIG["provider"] = "ABC"

    mock_prompt.return_value = "PROMPT"

    result = generate_answer(
        "Question",
        "Context",
        "History",
    )

    assert "Unsupported provider" in result


@patch("services.rag.get_prompt")
def test_outer_exception(mock_prompt):
    mock_prompt.side_effect = Exception("Boom")

    result = generate_answer(
        "Question",
        "Context",
        "History",
    )

    assert "Boom" in result

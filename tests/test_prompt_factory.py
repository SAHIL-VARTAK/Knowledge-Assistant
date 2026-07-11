from services.prompt_factory import get_prompt

QUESTION = "What is my name?"
CONTEXT = "My name is Sahil."
HISTORY = "User previously asked about personal details."


def assert_common_content(prompt: str):
    assert QUESTION in prompt
    assert CONTEXT in prompt
    assert HISTORY in prompt


def test_gemini_prompt():
    prompt = get_prompt(
        "Gemini",
        "gemini-2.5-flash",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "Do NOT use JSON." in prompt
    assert "QUESTION:" in prompt
    assert "ANSWER:" in prompt
    assert "SOURCES:" in prompt

    assert_common_content(prompt)


def test_phi_prompt():
    prompt = get_prompt(
        "Ollama",
        "phi4-mini",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "No JSON" in prompt
    assert "QUESTION:" in prompt
    assert "ANSWER:" in prompt
    assert "SOURCES:" in prompt

    assert_common_content(prompt)


def test_llama_prompt():
    prompt = get_prompt(
        "Ollama",
        "llama3.2:3b",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "Example response:" in prompt
    assert "Always return QUESTION, ANSWER and SOURCES" in prompt

    assert_common_content(prompt)


def test_qwen_prompt():
    prompt = get_prompt(
        "Ollama",
        "qwen3:4b",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "Give quick response" in prompt
    assert "No JSON." in prompt

    assert_common_content(prompt)


def test_gemma_prompt():
    prompt = get_prompt(
        "Ollama",
        "gemma3:1b",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "Reply EXACTLY like this example" in prompt
    assert "Do not use JSON." in prompt

    assert_common_content(prompt)


def test_unknown_model_falls_back_to_gemini():
    prompt = get_prompt(
        "Ollama",
        "unknown-model",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "Do NOT use JSON." in prompt
    assert_common_content(prompt)


def test_unknown_provider_falls_back_to_gemini():
    prompt = get_prompt(
        "Unknown",
        "unknown",
        QUESTION,
        CONTEXT,
        HISTORY,
    )

    assert "Do NOT use JSON." in prompt
    assert_common_content(prompt)

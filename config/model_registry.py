import os

MODEL_REGISTRY = {
    "Gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-pro"
    ],
    "Ollama": [
        "qwen3:4b",
        "gemma3:4b",
        "phi4-mini",
        "qwen3:8b"
    ]
}

CURRENT_CONFIG = {
    "provider": "Gemini",
    "model": "gemini-2.5-flash",
    "api_key": os.getenv("GEMINI_API_KEY")
}

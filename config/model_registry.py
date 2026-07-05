import os

MODEL_REGISTRY = {
    "Gemini": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "Ollama": ["phi4-mini", "gemma3:1b", "qwen3:4b", "llama3.2:3b"],
}

CURRENT_CONFIG = {"provider": "Gemini", "model": "gemini-2.5-flash", "api_key": os.getenv("GEMINI_API_KEY")}

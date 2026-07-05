import ollama
from google import genai

from config.model_registry import CURRENT_CONFIG
from services.prompt_factory import get_prompt


def generate_answer(question: str, context: str, history: str) -> str:
    prompt = get_prompt(
        provider=CURRENT_CONFIG["provider"],
        model=CURRENT_CONFIG["model"],
        question=question,
        context=context,
        history=history,
    )

    print(f"Generating response using {CURRENT_CONFIG['provider']} : {CURRENT_CONFIG['model']}")

    try:
        provider = CURRENT_CONFIG["provider"]
        model = CURRENT_CONFIG["model"]

        if provider == "Gemini":
            if provider == "Gemini":
                api_key = CURRENT_CONFIG["api_key"]

                if not api_key:
                    return f"""
                        QUESTION:
                        {question}
            
                        ANSWER:
                        Gemini API key is not configured. Please provide a valid API key from the sidebar.
            
                        SOURCES:
            
                        """.strip()

                try:
                    client = genai.Client(api_key=api_key)

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )

                    print(f"{model}:\n{response.text}")
                    return response.text

                except Exception as e:
                    return f"""
                        QUESTION:
                        {question}
            
                        ANSWER:
                        Failed to generate a response using Gemini: {str(e)}
            
                        SOURCES:
            
                        """.strip()

        elif provider == "Ollama":
            response = ollama.chat(model=model, format="json", messages=[{"role": "user", "content": prompt}])

            print(f"{model} : \n{response['message']['content']}")
            return response["message"]["content"]

        else:
            return f"Error generating answer: Unsupported provider '{provider}'"

    except Exception as e:
        return f"Error generating answer: {str(e)}"

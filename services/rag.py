from google import genai
from services.prompt_factory import get_prompt
from config.model_registry import CURRENT_CONFIG
import ollama


def generate_answer(
        question: str,
        context: str,
        history: str
) -> str:
    prompt = get_prompt(
        provider=CURRENT_CONFIG["provider"],
        model=CURRENT_CONFIG["model"],
        question=question,
        context=context,
        history=history
    )

    print(f'Generating response using {CURRENT_CONFIG["provider"]} : {CURRENT_CONFIG["model"]}')

    try:
        provider = CURRENT_CONFIG["provider"]
        model = CURRENT_CONFIG["model"]

        if provider == "Gemini":
            client = genai.Client(
                api_key=CURRENT_CONFIG["api_key"]
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"{model} : \n{response.text}")
            return response.text

        elif provider == "Ollama":
            response = ollama.chat(
                model=model,
                format="json",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            print(f'{model} : \n{response["message"]["content"]}')
            return response["message"]["content"]

        else:
            return (
                f"Error generating answer: "
                f"Unsupported provider '{provider}'"
            )

    except Exception as e:
        return (
            f"Error generating answer: {str(e)}"
        )

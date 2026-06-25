from google import genai
from config.model_registry import CURRENT_CONFIG
import ollama


def generate_answer(
        question: str,
        context: str,
        history: str
) -> str:
    prompt = f"""
        You are a document assistant.

        Answer ONLY using the provided context.

        Use the conversation history to understand references such as:
        - "it"
        - "that"
        - "the second one"
        - "tell me more"

        After answering, return the source filenames that were actually used.

        If the answer is not present in the documents, say:
        "I could not find that information in the uploaded documents."

        Return valid JSON only.

        Conversation History:
        {history}

        Document Context:
        {context}

        Current Question:
        {question}

        Format:
        {{
          "question": "user question",
          "answer": "...",
          "sources": ["file1.pdf"]
        }}
        """

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

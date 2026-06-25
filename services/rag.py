from dotenv import load_dotenv
from google import genai
from config.model_registry import CURRENT_CONFIG

load_dotenv()

client = genai.Client(
    api_key=CURRENT_CONFIG["api_key"]
)


def generate_answer(question: str, context: str, history: str) -> str:
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
        response = client.models.generate_content(
            model=CURRENT_CONFIG["model"],
            contents=prompt
        )
        print(response.text)

        return response.text

    except Exception as e:
        return f"Error generating answer: {str(e)}"

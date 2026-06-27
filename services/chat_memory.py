conversation_history = []


def add_message(role: str, content: str, sources = None):
    conversation_history.append({
        "role": role,
        "content": content,
        "source": sources or []
    })


def get_history():
    return conversation_history


def clear_history():
    conversation_history.clear()

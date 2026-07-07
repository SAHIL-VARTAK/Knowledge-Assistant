from services.chat_memory import (
    add_message,
    clear_history,
    get_history,
)


def setup_function():
    """Runs before every test."""
    clear_history()


def test_add_message():
    add_message(
        "user",
        "Hello",
        ["test.pdf"],
    )

    history = get_history()

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[0]["source"] == ["test.pdf"]


def test_add_message_without_sources():
    add_message(
        "assistant",
        "Hi",
    )

    history = get_history()
    assert history[0]["source"] == []


def test_get_history():
    add_message("user", "One")
    add_message("assistant", "Two")

    history = get_history()
    assert len(history) == 2


def test_clear_history():
    add_message("user", "Hello")
    clear_history()

    assert get_history() == []

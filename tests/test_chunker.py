from services.chunker import chunk_text


def test_empty_text():
    assert chunk_text("") == []


def test_small_text():
    text = "Hello World"

    assert chunk_text(text) == ["Hello World"]


def test_exact_chunk_size():
    text = "a" * 700

    chunks = chunk_text(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_multiple_chunks():
    text = "a" * 1500

    chunks = chunk_text(text)

    assert len(chunks) >= 2


def test_custom_chunk_size():
    text = "abcdefghij"

    chunks = chunk_text(
        text,
        chunk_size=4,
        overlap=0,
    )

    assert chunks == [
        "abcd",
        "efgh",
        "ij",
    ]


def test_overlap():
    text = "abcdefghij"

    chunks = chunk_text(
        text,
        chunk_size=4,
        overlap=2,
    )

    assert chunks == [
        "abcd",
        "cdef",
        "efgh",
        "ghij",
    ]


def test_newline_split():
    text = "Hello\nWorld\nPython\nTesting"

    chunks = chunk_text(
        text,
        chunk_size=12,
        overlap=0,
    )

    assert chunks[0] == "Hello\nWorld"

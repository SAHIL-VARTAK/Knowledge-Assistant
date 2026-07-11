from utils.ai_response_cleaner import parse_ai_response


def test_parse_standard_json():
    response = """
    {
        "QUESTION": "What is AI?",
        "ANSWER": "Artificial Intelligence",
        "SOURCES": "doc1.pdf,doc2.pdf"
    }
    """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "What is AI?"
    assert result["answer"] == "Artificial Intelligence"
    assert result["sources"] == ["doc1.pdf", "doc2.pdf"]


def test_parse_json_sources_list():
    response = """
    {
        "QUESTION": "Question",
        "ANSWER": "Answer",
        "SOURCES": ["a.pdf", "b.pdf"]
    }
    """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "Question"
    assert result["answer"] == "Answer"
    assert result["sources"] == ["a.pdf", "b.pdf"]


def test_parse_llama_json():
    response = """
    {
        "What is my name?": "SAHIL VARTAK"
    }
    """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "What is my name?"
    assert result["answer"] == "SAHIL VARTAK"
    assert result["sources"] == []


def test_parse_question_answer_sources():
    response = """
        QUESTION:
        What is AI?
        
        ANSWER:
        Artificial Intelligence
        
        SOURCES:
        doc1.pdf,doc2.pdf
        """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "What is AI?"
    assert result["answer"] == "Artificial Intelligence"
    assert result["sources"] == ["doc1.pdf", "doc2.pdf"]


def test_parse_multiline_answer():
    response = """
        QUESTION:
        Explain AI
        
        ANSWER:
        Line one.
        Line two.
        Line three.
        
        SOURCES:
        doc.pdf
        """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "Explain AI"
    assert result["answer"] == "Line one.\nLine two.\nLine three."
    assert result["sources"] == ["doc.pdf"]


def test_parse_multiline_question():
    response = """
        QUESTION:
        What is
        Artificial Intelligence?
        
        ANSWER:
        AI
        
        SOURCES:
        doc.pdf
        """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "What is\nArtificial Intelligence?"
    assert result["answer"] == "AI"


def test_parse_multiline_sources():
    response = """
        QUESTION:
        Test
        
        ANSWER:
        Answer
        
        SOURCES:
        a.pdf
        b.pdf
        c.pdf
        """

    result = parse_ai_response(response, "Fallback")

    assert result["sources"] == ["a.pdf", "b.pdf", "c.pdf"]


def test_parse_invalid_json_falls_back():
    response = """
        {
        invalid json
        
        QUESTION:
        Test
        
        ANSWER:
        Answer
        
        SOURCES:
        doc.pdf
        """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "Test"
    assert result["answer"] == "Answer"
    assert result["sources"] == ["doc.pdf"]


def test_parse_missing_question_uses_fallback():
    response = """
        ANSWER:
        Answer only
        
        SOURCES:
        doc.pdf
        """

    result = parse_ai_response(response, "Original Question")

    assert result["question"] == "Original Question"
    assert result["answer"] == "Answer only"
    assert result["sources"] == ["doc.pdf"]


def test_parse_empty_response():
    result = parse_ai_response("", "Fallback Question")

    assert result["question"] == "Fallback Question"
    assert result["answer"] == ""
    assert result["sources"] == []


def test_parse_inline_sections():
    response = """
        QUESTION: What is AI?
        ANSWER: Artificial Intelligence
        SOURCES: doc1.pdf,doc2.pdf
        """

    result = parse_ai_response(response, "Fallback")

    assert result["question"] == "What is AI?"
    assert result["answer"] == "Artificial Intelligence"
    assert result["sources"] == ["doc1.pdf", "doc2.pdf"]

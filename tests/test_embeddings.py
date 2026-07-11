from unittest.mock import patch

from services.embeddings import create_embeddings


@patch("services.embeddings.model")
def test_create_embeddings_single_text(mock_model):
    mock_model.encode.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]

    result = create_embeddings(["Hello"])

    assert result == [[0.1, 0.2, 0.3]]

    mock_model.encode.assert_called_once_with(["Hello"])


@patch("services.embeddings.model")
def test_create_embeddings_multiple_texts(mock_model):
    mock_model.encode.return_value.tolist.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    texts = [
        "Hello",
        "World",
    ]

    result = create_embeddings(texts)

    assert result == [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    mock_model.encode.assert_called_once_with(texts)


@patch("services.embeddings.model")
def test_create_embeddings_empty_list(mock_model):
    mock_model.encode.return_value.tolist.return_value = []

    result = create_embeddings([])

    assert result == []

    mock_model.encode.assert_called_once_with([])

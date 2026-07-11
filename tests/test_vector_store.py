from unittest.mock import patch

from services.vector_store import (
    clear_collection,
    get_sources,
    save_chunks,
    search_documents,
)


@patch("services.vector_store.collection")
@patch("services.vector_store.create_embeddings")
@patch("services.vector_store.uuid.uuid4")
def test_save_chunks(
    mock_uuid,
    mock_embeddings,
    mock_collection,
):
    chunks = [
        "chunk1",
        "chunk2",
    ]

    mock_embeddings.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    mock_uuid.side_effect = [
        "id1",
        "id2",
    ]

    save_chunks(
        chunks,
        "resume.pdf",
    )

    mock_embeddings.assert_called_once_with(chunks)

    mock_collection.add.assert_called_once()


@patch("services.vector_store.collection")
@patch("services.vector_store.create_embeddings")
@patch("services.vector_store.uuid.uuid4")
def test_save_chunks_arguments(
    mock_uuid,
    mock_embeddings,
    mock_collection,
):
    chunks = ["a", "b"]

    mock_embeddings.return_value = [
        [1],
        [2],
    ]

    mock_uuid.side_effect = [
        "id1",
        "id2",
    ]

    save_chunks(
        chunks,
        "resume.pdf",
    )

    kwargs = mock_collection.add.call_args.kwargs

    assert kwargs["ids"] == [
        "id1",
        "id2",
    ]

    assert kwargs["documents"] == chunks

    assert kwargs["embeddings"] == [
        [1],
        [2],
    ]

    assert kwargs["metadatas"] == [
        {"source": "resume.pdf"},
        {"source": "resume.pdf"},
    ]


@patch("services.vector_store.collection")
@patch("services.vector_store.create_embeddings")
def test_search_documents(
    mock_embeddings,
    mock_collection,
):
    mock_embeddings.return_value = [
        [0.1],
    ]

    expected = {
        "documents": [["doc"]],
    }

    mock_collection.query.return_value = expected

    result = search_documents("AI")

    assert result == expected

    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1]],
        n_results=10,
    )


@patch("services.vector_store.collection")
def test_get_sources(mock_collection):
    mock_collection.get.return_value = {
        "metadatas": [
            {"source": "resume.pdf"},
            {"source": "notes.pdf"},
            {"source": "resume.pdf"},
            {},
            None,
        ]
    }

    sources = get_sources()

    assert sources == [
        "notes.pdf",
        "resume.pdf",
    ]


@patch("services.vector_store.collection")
def test_get_sources_empty(mock_collection):
    mock_collection.get.return_value = {
        "metadatas": [],
    }

    assert get_sources() == []


@patch("services.vector_store.client")
def test_clear_collection(mock_client):
    clear_collection()

    mock_client.delete_collection.assert_called_once_with("documents")

    mock_client.get_or_create_collection.assert_called_once_with(name="documents")

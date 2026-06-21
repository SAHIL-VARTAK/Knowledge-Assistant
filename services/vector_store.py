import chromadb
import uuid

from services.embeddings import create_embeddings

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


def save_chunks(chunks, filename):
    embeddings = create_embeddings(chunks)

    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {"source": filename}
            for _ in chunks
        ]
    )


def search_documents(query):

    query_embedding = create_embeddings(
        [query]
    )

    return collection.query(
        query_embeddings=query_embedding,
        n_results=10
    )

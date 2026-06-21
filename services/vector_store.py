import chromadb
import uuid

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


def save_chunks(chunks, filename):
    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=chunks,
        metadatas=[
            {"source": filename}
            for _ in chunks
        ]
    )


def search_documents(query):
    return collection.query(
        query_texts=[query],
        n_results=3
    )
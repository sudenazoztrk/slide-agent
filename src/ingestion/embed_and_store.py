import json
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
import uuid
import os

NAMESPACE = uuid.NAMESPACE_DNS

def make_point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, chunk_id))


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
client = QdrantClient(host=QDRANT_HOST, port=6333)

COLLECTION_NAME = "slayt_agent"
VECTOR_SIZE = 1024

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print(f"'{COLLECTION_NAME}' koleksiyonu oluşturuldu.")
else:
    print(f"'{COLLECTION_NAME}' koleksiyonu zaten var, atlanıyor.")


def load_chunks(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_text(text: str) -> list[float]:
    response = ollama.embeddings(model="bge-m3", prompt=text)
    return response["embedding"]

def store_chunks(chunks: list[dict]) -> int:
    points = []
    for chunk in chunks:
        vector = embed_text(chunk["text"])
        point_id = make_point_id(chunk["id"])
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "chunk_id": chunk["id"],
                "text": chunk["text"],
                "source": chunk["metadata"]["source"],
                "slide_number": chunk["metadata"]["slide_number"]
            }
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)

if __name__ == "__main__":
    chunks = load_chunks("data/processed/KNN_chunks.json")
    count = store_chunks(chunks)
    print(f"\nToplam {count} chunk Qdrant'a kaydedildi.")
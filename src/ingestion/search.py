from qdrant_client import QdrantClient
import ollama

client = QdrantClient(host="localhost", port=6333) #qdrant'a bağlan
COLLECTION_NAME = "slayt_agent" 


def embed_text(text: str) -> list[float]:
    response = ollama.embeddings(model="bge-m3", prompt=text)
    return response["embedding"]


def search(query: str, top_k: int = 3):
    query_vector = embed_text(query) # soruyu embed et

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )

    return results.points


if __name__ == "__main__":
    question = "What is lazy learning?" 
    hits = search(question)

    for hit in hits:
        print(f"Skor: {hit.score:.4f} | Slayt {hit.payload['slide_number']}")
        print(hit.payload['text'][:100])
        print("---")
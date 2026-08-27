def create_chunks(slides: list[dict], source_name: str) -> list[dict]:
    chunks = []

    for slide in slides:
        chunk_id = f"{source_name}_slide_{slide['slide_number']}" # her sayfa için benzersiz id
        chunks.append({
            "id": chunk_id,
            "text": slide["text"],
            "metadata": {
                "source": source_name,
                "slide_number": slide["slide_number"]
            }
        })

    return chunks
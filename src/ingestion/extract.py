import json
import pymupdf as fitz


def extract_slides(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    slides = []

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        slides.append({
            "slide_number": i + 1,
            "text": text
        })

    return slides


def save_slides(slides: list[dict], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(slides, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    from chunking_process import create_chunks

    slides = extract_slides("data/raw/KNN.pdf")
    chunks = create_chunks(slides, source_name="KNN")
    save_slides(chunks, "data/processed/KNN_chunks.json")
    print(f"{len(chunks)} chunk data/processed/KNN_chunks.json dosyasına kaydedildi.")
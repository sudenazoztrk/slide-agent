import re
import ollama
from src.retrieval.search import search

def build_prompt(question: str, hits: list) -> str:
    context_parts = []
    for hit in hits:
        slide_num = hit.payload["slide_number"]
        text = hit.payload["text"]
        context_parts.append(f"[Slayt {slide_num}]\n{text}")

    context = "\n\n".join(context_parts)

    prompt = f"""Aşağıda ders slaytlarından alınmış bazı içerikler var. SADECE bu içeriklere dayanarak soruyu cevapla. Eğer cevap bu içeriklerde yoksa, "Bu bilgi verilen slaytlarda yok" de, kendi bilgini uydurma.

{context}

Soru: {question}
Cevap:"""

    return prompt


def generate_answer(question: str, top_k: int = 3) -> str:
    hits = search(question, top_k=top_k)
    prompt = build_prompt(question, hits)

    response = ollama.chat(
        model="qwen3",
        messages=[{"role": "user", "content": prompt}],
        think=False
    )

    answer = response["message"]["content"]
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()

    return answer, hits


if __name__ == "__main__":
    question = "What is the transformer attention mechanism?"
    answer, hits = generate_answer(question)

    print("Cevap:")
    print(answer)
    print("\nKaynak slaytlar:", [h.payload["slide_number"] for h in hits])
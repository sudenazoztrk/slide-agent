import re
import ollama


def build_context(result: dict) -> str:
    slides = result["retrieved_slides"]
    web_results = result.get("web_results", "")

    slide_context = "\n\n".join(
        f"[Slayt {s['slide_number']}]\n{s['text']}" for s in slides
    )

    if web_results:
        return f"{slide_context}\n\n[Web Kaynakları]\n{web_results}"
    return slide_context


def judge_faithfulness(question: str, context: str, answer: str) -> dict:
    prompt = f"""Sen bir RAG sisteminin cevaplarını denetleyen bir hakemsin.
Görevin: aşağıdaki CEVAP'ın, sadece verilen CONTEXT'e dayanıp dayanmadığını değerlendirmek.
CONTEXT'in kendisinin doğru olup olmadığını değerlendirme, sadece CEVAP'ın CONTEXT'te olmayan bir bilgi uydurup uydurmadığına bak.

CONTEXT:
{context}

SORU: {question}

CEVAP: {answer}

CEVAP, CONTEXT'te olmayan hiçbir bilgi eklemeden, tamamen CONTEXT'e dayanarak mı yazılmış?
İlk satıra sadece SADIK ya da UYDURMA_VAR yaz.
İkinci satıra tek cümlelik kısa bir gerekçe yaz."""

    response = ollama.chat(
        model="qwen3",
        messages=[{"role": "user", "content": prompt}],
        think=False
    )

    raw = response["message"]["content"]
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    lines = raw.split("\n", 1)
    verdict_line = lines[0].strip().upper()
    reason = lines[1].strip() if len(lines) > 1 else ""

    is_faithful = "SADIK" in verdict_line and "UYDURMA" not in verdict_line

    return {"faithful": is_faithful, "reason": reason}


if __name__ == "__main__":
    from src.agent.graph import app

    result = app.invoke({"question": "What is the fundamental difference between Eager Learning and Instance-Based (Lazy) Learning in terms of when the target function is constructed?"})
    context = build_context(result)
    verdict = judge_faithfulness(result["question"], context, result["answer"])

    print(f"Sadık mı: {verdict['faithful']}")
    print(f"Gerekçe: {verdict['reason']}")
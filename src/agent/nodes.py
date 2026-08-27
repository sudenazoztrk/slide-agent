from src.retrieval.search import search
import re
import ollama
from ddgs import DDGS



def retrieve(state: dict) -> dict:
    question = state["question"]
    hits = search(question, top_k=3)

    retrieved_slides = [
        {
            "slide_number": hit.payload["slide_number"],
            "source": hit.payload["source"],
            "text": hit.payload["text"],
            "score": hit.score,
        }
        for hit in hits
    ]

    return {"retrieved_slides": retrieved_slides}

def grade(state: dict) -> dict:
    question = state["question"]
    slides = state["retrieved_slides"]

    context = "\n\n".join(
        f"[Slayt {s['slide_number']}]\n{s['text']}" for s in slides
    )

    prompt = f"""Aşağıda bir soru ve o soruyla ilgili olabilecek slayt içerikleri var.

    {context}

    Soru: {question}

    Bu slayt içerikleri, yukarıdaki soruyu doğru ve eksiksiz cevaplamak için yeterli mi?
    Sadece tek kelime yaz: EVET ya da HAYIR. Başka hiçbir şey yazma."""

    response = ollama.chat(
        model="qwen3",
        messages=[{"role": "user", "content": prompt}],
        think=False
    )

    raw_answer = response["message"]["content"]
    raw_answer = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()

    is_sufficient = "EVET" in raw_answer.upper()

    return {"context_sufficient": is_sufficient}



def web_search(state: dict) -> dict:
    question = state["question"]

    results = DDGS().text(question, max_results=3)

    combined = "\n\n".join(
        f"{r['title']}\n{r['body']}" for r in results
    )

    return {"web_results": combined}

def generate(state: dict) -> dict:
    question = state["question"]
    slides = state["retrieved_slides"]
    web_results = state.get("web_results", "")

    slide_context = "\n\n".join(
        f"[Slayt {s['slide_number']}]\n{s['text']}" for s in slides
    )

    if web_results:
        full_context = f"{slide_context}\n\n[Web Kaynakları]\n{web_results}"
        instruction = "Aşağıda ders slaytlarından ve web'den alınmış içerikler var. Bu içeriklere dayanarak soruyu cevapla. Cevabında hangi bilginin slayttan, hangisinin web'den geldiğini belirt."
    else:
        full_context = slide_context
        instruction = "Aşağıda ders slaytlarından alınmış içerikler var. SADECE bu içeriklere dayanarak soruyu cevapla."

    prompt = f"""{instruction}

{full_context}

Soru: {question}
Cevap:"""

    response = ollama.chat(
        model="qwen3",
        messages=[{"role": "user", "content": prompt}],
        think=False
    )

    answer = response["message"]["content"]
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()

    return {"answer": answer}

if __name__ == "__main__":
    for question in ["What is lazy learning?", "What is the transformer attention mechanism?"]:
        state = {"question": question}
        state.update(retrieve(state))
        state.update(grade(state))

        if not state["context_sufficient"]:
            state.update(web_search(state))

        state.update(generate(state))

        print(f"Soru: {question}")
        print(f"Yeterli mi: {state['context_sufficient']}")
        print(f"Cevap: {state['answer']}")
        print("=" * 50)
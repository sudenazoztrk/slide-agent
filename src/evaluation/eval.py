import json
from src.agent.graph import app


def load_questions(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_routing_eval(questions: list[dict]):
    results = []

    for q in questions:
        result = app.invoke({"question": q["question"]})
        actual = result["context_sufficient"]
        expected = q["should_use_slides"]

        results.append({
            "id": q["id"],
            "question": q["question"],
            "expected": expected,
            "actual": actual,
            "correct": actual == expected
        })

    correct_count = sum(r["correct"] for r in results)
    accuracy = correct_count / len(results)

    return accuracy, results


if __name__ == "__main__":
    questions = load_questions("data/eval/questions.json")
    accuracy, results = run_routing_eval(questions)

    for r in results:
        status = "DOĞRU" if r["correct"] else "YANLIŞ"
        print(f"[{status}] {r['id']}: beklenen={r['expected']}, gerçek={r['actual']} — {r['question']}")

    print(f"\nRouting Accuracy: {accuracy:.2%} ({sum(r['correct'] for r in results)}/{len(results)})")
import json
from src.agent.graph import app
from src.evaluation.judge import build_context, judge_faithfulness


def load_questions(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_full_eval(questions: list[dict]):
    results = []

    for q in questions:
        result = app.invoke({"question": q["question"]})

        actual_routing = result["context_sufficient"]
        expected_routing = q["should_use_slides"]

        context = build_context(result)
        verdict = judge_faithfulness(q["question"], context, result["answer"])

        results.append({
            "id": q["id"],
            "question": q["question"],
            "expected_routing": expected_routing,
            "actual_routing": actual_routing,
            "routing_correct": actual_routing == expected_routing,
            "faithful": verdict["faithful"],
            "faithfulness_reason": verdict["reason"],
        })

    return results


def print_report(results: list[dict]):
    for r in results:
        routing_status = "DOĞRU" if r["routing_correct"] else "YANLIŞ"
        faith_status = "SADIK" if r["faithful"] else "UYDURMA"

        print(f"[{r['id']}] {r['question']}")
        print(f"  Routing: {routing_status} (beklenen={r['expected_routing']}, gerçek={r['actual_routing']})")
        print(f"  Faithfulness: {faith_status} — {r['faithfulness_reason']}")
        print("---")

    total = len(results)
    routing_accuracy = sum(r["routing_correct"] for r in results) / total
    faithfulness_rate = sum(r["faithful"] for r in results) / total

    print(f"\nRouting Accuracy: {routing_accuracy:.2%}")
    print(f"Faithfulness Rate: {faithfulness_rate:.2%}")


if __name__ == "__main__":
    questions = load_questions("data/eval/questions.json")
    results = run_full_eval(questions)
    print_report(results)
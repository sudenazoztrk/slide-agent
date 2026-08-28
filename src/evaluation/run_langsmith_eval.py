from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from src.agent.graph import app
from src.evaluation.judge import build_context, judge_faithfulness

DATASET_NAME = "slide-agent-eval"


def target(inputs: dict) -> dict:
    result = app.invoke({"question": inputs["question"]})
    context = build_context(result)

    return {
        "context_sufficient": result["context_sufficient"],
        "answer": result["answer"],
        "context": context,
    }


def routing_accuracy(outputs: dict, reference_outputs: dict) -> dict:
    correct = outputs["context_sufficient"] == reference_outputs["should_use_slides"]
    return {"key": "routing_accuracy", "score": correct}


def faithfulness(inputs: dict, outputs: dict) -> dict:
    verdict = judge_faithfulness(inputs["question"], outputs["context"], outputs["answer"])
    return {"key": "faithfulness", "score": verdict["faithful"], "comment": verdict["reason"]}


if __name__ == "__main__":
    client = Client()
    client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[routing_accuracy, faithfulness],
        experiment_prefix="slide-agent",
    )

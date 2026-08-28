from dotenv import load_dotenv
load_dotenv()
import json
from langsmith import Client

client = Client()
DATASET_NAME = "slayt-agent-eval"


def load_questions(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_or_get_dataset():
    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' zaten var, mevcut olan kullanılıyor.")
        return client.read_dataset(dataset_name=DATASET_NAME)

    dataset = client.create_dataset(dataset_name=DATASET_NAME)
    print(f"Dataset '{DATASET_NAME}' oluşturuldu.")
    return dataset


def upload_examples(dataset, questions: list[dict]):
    for q in questions:
        client.create_example(
            dataset_id=dataset.id,
            inputs={"question": q["question"]},
            outputs={"should_use_slides": q["should_use_slides"]},
            metadata={"id": q["id"]}
        )
    print(f"{len(questions)} örnek dataset'e yüklendi.")


if __name__ == "__main__":
    questions = load_questions("data/eval/questions.json")
    dataset = create_or_get_dataset()
    upload_examples(dataset, questions)
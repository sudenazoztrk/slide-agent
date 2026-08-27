from typing import TypedDict


class AgentState(TypedDict):
    question: str
    retrieved_slides: list[dict]
    context_sufficient: bool
    web_results: str
    answer: str
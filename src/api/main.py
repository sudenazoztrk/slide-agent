from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from src.agent.graph import app as agent_app
import os


app = FastAPI(title="Slayt Agent API")


def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("MY_API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Geçersiz API key")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    context_sufficient: bool
    slides_used: list[int]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask", dependencies=[Depends(verify_api_key)])
def ask(request: AskRequest) -> AskResponse:
    result = agent_app.invoke({"question": request.question})
    slides_used = [s["slide_number"] for s in result["retrieved_slides"]]

    return AskResponse(
        answer=result["answer"],
        context_sufficient=result["context_sufficient"],
        slides_used=slides_used
    )
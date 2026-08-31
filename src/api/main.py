from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Header, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from src.agent.graph import app as agent_app
import os
from pathlib import Path
import shutil

from src.ingestion.extract import extract_slides
from src.ingestion.chunking_process import create_chunks
from src.ingestion.embed_and_store import store_chunks


app = FastAPI(title="Slayt Agent API")

class SlideReference(BaseModel):
    source: str
    slide_number: int

def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("MY_API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Geçersiz API key")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    context_sufficient: bool
    slides_used: list[SlideReference]

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask", dependencies=[Depends(verify_api_key)])
def ask(request: AskRequest) -> AskResponse:
    result = agent_app.invoke({"question": request.question})
    slides_used = [
        SlideReference(source=s["source"], slide_number=s["slide_number"])
        for s in result["retrieved_slides"]
    ]

    return AskResponse(
        answer=result["answer"],
        context_sufficient=result["context_sufficient"],
        slides_used=slides_used
    )

@app.post("/upload", dependencies=[Depends(verify_api_key)])
def upload_pdf(file: UploadFile = File(...)):
    upload_dir = Path("data/raw")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    source_name = file_path.stem

    slides = extract_slides(str(file_path))
    chunks = create_chunks(slides, source_name=source_name)
    chunks_stored = store_chunks(chunks)

    return {
        "filename": file.filename,
        "source": source_name,
        "slides_processed": len(slides),
        "chunks_stored": chunks_stored
    }
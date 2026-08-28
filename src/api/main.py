from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.graph import app as agent_app

app = FastAPI(title="Slayt Agent API") # API'ın ana nesnesi

class AskRequest(BaseModel):
    question: str
"""
bu, Pydantic'in temel yapı taşı. BaseModel'den miras alan bir sınıf tanımlıyoruz,
 içine hangi alanların (question: str) bekleneceğini yazıyoruz. FastAPI, /ask adresine bir istek geldiğinde, 
 gelen JSON'ı otomatik olarak bu şablona göre doğruluyor — eğer question alanı yoksa, ya da string değilse, 
 FastAPI otomatik olarak anlamlı bir hata mesajı döndürüyor, bizim elle kontrol yazmamıza hiç gerek kalmıyor.
"""

class AskResponse(BaseModel):
    answer: str
    context_sufficient: bool
    slides_used: list[int]
"""
aynı mantık ama bu sefer bizim döndüreceğimiz cevabın şeklini tanımlıyoruz: 
answer (string), context_sufficient (bool), slides_used (int listesi — hangi slaytların kullanıldığı, 
projenin başından beri istediğin "kaynak gösterme" özelliği burada API seviyesinde somutlaşıyor).
"""

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask")
def ask(request: AskRequest) -> AskResponse:
    result = agent_app.invoke({"question": request.question})

    slides_used = [s["slide_number"] for s in result["retrieved_slides"]]

    return AskResponse(
        answer=result["answer"],
        context_sufficient=result["context_sufficient"],
        slides_used=slides_used
    )


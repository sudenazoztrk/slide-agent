# Paper Pilot

Akademik makaleler ve teknik dokümanlar üzerinde çalışan, çok adımlı (agentic)
bir araştırma asistanı. Amaç sadece "çalışan bir demo" yapmak değil; production
bir AI sisteminde karşına çıkacak her katmanı (RAG, agent orchestration,
evaluation/guardrails, model serving, MLOps, deployment) tek bir projede
uçtan uca deneyimlemek.

## Neden bu proje?

Klasik bir "chatbot with RAG" demosu ile bir AI Engineer'ın gerçekte
uğraştığı problemler arasında büyük fark var. Bu fark genelde şurada:
- Vector search'ün tek başına yetmediği, agent'ın *ne zaman* hangi tool'u
  çağıracağına karar vermesi gereken durumlar
- "Model doğru cevap verdi mi?" sorusunu insan gözüyle değil, otomatik
  metriklerle (RAGAS, LLM-as-judge) cevaplayabilmek
- Aynı sistemi hem pahalı bir API modeliyle hem de ucuz/local bir modelle
  çalıştırıp trade-off'u somut sayılarla görebilmek
- Kodun bir Jupyter notebook'ta değil, testi olan, container'a alınmış,
  CI'dan geçen bir serviste yaşaması

Bu proje bu beş noktayı sırayla inşa ediyor.

## Mimari (özet)

```
Ingestion pipeline  ->  Vector store  ->  Agent (LangGraph)  ->  Evaluation & guardrails  ->  Serving
   (PDF/web -> chunk)     (Qdrant)         (tool use + reasoning)   (RAGAS, LLM-as-judge)    (FastAPI + Docker)
```

Her ok, bir önceki bileşenin çıktısını bir sonrakinin girdisine dönüştüren
gerçek bir arayüz (interface); yani her bileşeni birbirinden bağımsız
test edebiliyor, birini değiştirdiğimizde diğerlerini bozmuyoruz. Bu,
"her şeyi tek bir script'te yaz" yaklaşımının tam tersi ve production
kodunun neden bu şekilde bölündüğünün pratik kanıtı olacak.

## Fazlar (roadmap)

1. **Kickoff & mimari** (bu commit) — proje iskeleti, FastAPI health-check,
   Docker, temel CI.
2. **Production RAG + vector store** — ingestion pipeline, chunking, Qdrant,
   hybrid search.
3. **Agent orchestration & tool use** — LangGraph ile çok adımlı agent,
   tool tanımları, (mümkünse) MCP.
4. **Evaluation & guardrails** — RAGAS metrikleri, golden dataset, hallucination
   kontrolü, prompt injection savunması.
5. **Model serving & fine-tuning deneyi** — API model vs local quantized model
   kıyası, küçük bir alt-görev için LoRA fine-tune.
6. **MLOps & deployment** — MLflow/DVC, Docker Compose, monitoring, (opsiyonel)
   Kubernetes.

## Klasör yapısı

```
paper-pilot/
  app/            -> FastAPI uygulaması (Faz ilerledikçe ingestion/, agent/, eval/ alt paketleri eklenecek)
  docker/         -> Dockerfile ve docker-compose.yml
  tests/          -> pytest testleri
  .github/workflows/ -> CI pipeline (lint + test, her push'ta otomatik çalışır)
```

Bu yapıyı seçtik çünkü `app/` içindeki her alt paket (ingestion, agent, eval)
kendi sorumluluğunu taşıyacak (single responsibility) ve birbirine sadece
net fonksiyon imzaları üzerinden bağlanacak — bu da hem test yazmayı
kolaylaştırıyor hem de "bu bug hangi katmanda" sorusuna hızlı cevap
verdiriyor.

## Yerelde çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Sonra `http://localhost:8000/health` adresine gidip `{"status": "ok"}`
cevabını görmen yeterli — bu, Faz 0'ın tek hedefi: "iskelet ayakta duruyor
ve dışarıdan sağlığı sorgulanabiliyor".

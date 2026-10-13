from fastapi import FastAPI

from app.api.schemas import Recommendation

app = FastAPI(title="RealTime RecSys")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/recommendations", response_model=list[Recommendation])
def recommendations(session_id: str, k: int = 10):
    # Día 1: datos fijos. En el día 3 se reemplaza por el recomendador real.
    return [Recommendation(product_id=1, score=0.9), Recommendation(product_id=2, score=0.5)]

# RealTime RecSys

Sistema de recomendación en tiempo real para e-commerce: recomienda productos que se ajustan a lo que el usuario hace **durante su sesión**.

**Stack:** Python 3.12 · FastAPI · AWS Lambda · S3 · LangChain
**Desarrollo local:** moto (S3) · AWS SAM local (Lambda) · Ollama (embeddings), sin costo ni cuenta de AWS.

> 🚧 En construcción. Plan día por día en [`docs/PLAN.md`](docs/PLAN.md).

## El problema
Las plataformas de e-commerce pierden ventas porque sus recomendaciones no reaccionan al comportamiento del usuario en tiempo real.

## Correr en local
```bash
uv sync
uv run uvicorn app.api.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

## Tests
```bash
uv run pytest -v
uv run ruff check .
```

## Progreso
- [x] Día 1 — FastAPI corriendo
- [ ] Día 2 — Artefactos de recomendación
- [ ] Día 3 — Recomendaciones en tiempo real + tests
- [ ] Día 4 — Artefactos desde S3 local (moto)
- [ ] Día 5 — Lambda local con `sam local`
- [ ] Día 6 — Búsqueda con LangChain + Ollama
- [ ] Día 7 — CI + README
- [ ] Día 8 (opcional) — Despliegue real en AWS

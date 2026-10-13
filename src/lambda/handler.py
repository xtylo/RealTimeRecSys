"""AWS Lambda entry point.

Mangum translates API Gateway (HTTP API, payload v2) events into ASGI requests,
so the same FastAPI app runs locally with uvicorn and on AWS Lambda.

Note: this folder is called `lambda`, which is a Python keyword, so it is NOT an
importable package. `src/scripts/build_lambda.py` copies this file to the root of
the deployment package, where Lambda loads it as the `handler` module
(Lambda handler setting: "handler.handler").
"""

from mangum import Mangum

from app.main import app

# lifespan="off": Mangum would otherwise run the FastAPI lifespan on EVERY invocation.
# Expensive initialization (loading model artifacts, creating clients) goes at module
# level instead: Lambda runs it once per cold start and reuses it while the instance is warm.
handler = Mangum(app, lifespan="off")

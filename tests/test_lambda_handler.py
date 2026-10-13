"""Invoke the Lambda handler in-process with an API Gateway HTTP API (v2) event."""

import importlib.util
import json
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# `lambda` is a Python keyword, so these files are loaded by path instead of imported.
lambda_handler = load_module("lambda_handler", SRC / "lambda" / "handler.py")
invoke_lambda = load_module("invoke_lambda", SRC / "scripts" / "invoke_lambda.py")


class FakeLambdaContext:
    function_name = "realtime-recsys-test"


def test_health_through_lambda_handler():
    event = invoke_lambda.build_event("GET", "/health")
    response = lambda_handler.handler(event, FakeLambdaContext())
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"status": "ok"}


def test_validation_error_through_lambda_handler():
    event = invoke_lambda.build_event("GET", "/recommendations?session_id=s1&k=abc")
    response = lambda_handler.handler(event, FakeLambdaContext())
    assert response["statusCode"] == 422

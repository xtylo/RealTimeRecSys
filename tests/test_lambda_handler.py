"""Invoke the Lambda handler in-process with an API Gateway HTTP API (v2) event."""

import importlib.util
import json
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# `lambda` is a Python keyword, so these files are loaded by path instead of imported.
invoke_lambda = load_module("invoke_lambda", SRC / "scripts" / "invoke_lambda.py")


class FakeLambdaContext:
    function_name = "realtime-recsys-test"


@pytest.fixture
def handler():
    # Loaded inside a fixture so the autouse `local_artifacts` fixture runs first (cold start).
    return load_module("lambda_handler", SRC / "lambda" / "handler.py").handler


def call(handler, method, path, body=None):
    response = handler(invoke_lambda.build_event(method, path, body), FakeLambdaContext())
    return response["statusCode"], json.loads(response["body"])


def test_health_through_lambda_handler(handler):
    assert call(handler, "GET", "/health") == (200, {"status": "ok"})


def test_validation_error_through_lambda_handler(handler):
    status, _ = call(handler, "GET", "/recommendations?session_id=s1&k=abc")
    assert status == 422


def test_session_survives_between_warm_invocations(handler):
    event = json.dumps({"session_id": "s1", "product_id": 1, "event_type": "view"})
    call(handler, "POST", "/events", event)
    _, body = call(handler, "GET", "/recommendations?session_id=s1&k=2")
    assert [r["product_id"] for r in body] == [2, 3]

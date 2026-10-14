import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def local_artifacts(tmp_path, monkeypatch):
    """Tiny model on disk + a clean, local-only environment for every test."""
    (tmp_path / "related.json").write_text(json.dumps({"1": [2, 3]}))
    (tmp_path / "popular.json").write_text(json.dumps([9, 8]))
    monkeypatch.setenv("ARTIFACTS_SOURCE", "local")
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("ENABLE_SEARCH", raising=False)
    return tmp_path


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as test_client:  # "with" runs the lifespan (init_state)
        yield test_client

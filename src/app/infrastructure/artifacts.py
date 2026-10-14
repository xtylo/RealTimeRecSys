import json
import os
from pathlib import Path


def load_artifacts() -> tuple[dict[str, list[int]], list[int]]:
    base = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))

    def read(name: str):
        return json.loads((base / name).read_text())

    return read("related.json"), read("popular.json")

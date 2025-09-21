import json
from pathlib import Path
from typing import Any

def load_json_with_fallback(*paths: str) -> Any:
    for p in paths:
        path = Path(p)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"No JSON found in: {paths}")

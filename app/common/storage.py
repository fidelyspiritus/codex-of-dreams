# app/common/storage.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Optional

def load_json_with_fallback(*paths: str) -> Any:
    """
    Try paths in order and return parsed JSON of the first existing file.
    Raises FileNotFoundError if none exist.
    """
    for p in paths:
        path = Path(p)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"No JSON found in: {paths}")

def try_load_json(path: str | Path) -> Optional[Any]:
    """
    Soft loader: return parsed JSON or None if file doesn't exist or invalid.
    Useful for optional debug screens/tests; keep IO under 'common.storage'.
    """
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_json(path: str | Path):
    path = Path(path)
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)
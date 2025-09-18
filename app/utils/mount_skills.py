# app/utils/mount_skills.py
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Literal, Dict


ROOT_DIR = Path(__file__).resolve().parents[1]   # .../app
DATA_DIR = ROOT_DIR.parent / "data" / "mount_skills"
ASSETS_DIR = ROOT_DIR.parent / "assets" / "mount_skills"

MountType = Literal["spears", "infantry", "archers"]

@dataclass
class Skill:
    id: str
    name: str
    type: str
    description: str
    image: str  # relative path, e.g. "spears/ragebeast_soul.png"

@dataclass
class MountSkills:
    mount_type: MountType
    slot1: List[Skill]
    slot2: List[Skill]

def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _normalize(raw_list: List[dict]) -> List[Skill]:
    return [
        Skill(
            id=s["id"],
            name=s["name"],
            type=s["type"],
            description=s["description"],
            image=s["image"],
        )
        for s in raw_list
    ]

@lru_cache(maxsize=3)
def load_mount(mount_type: MountType) -> MountSkills:
    """Загрузка одного типа коней (spears/infantry/archers) из JSON."""
    file_map: Dict[MountType, str] = {
        "spears": "spears.json",
        "infantry": "infantry.json",
        "archers": "archers.json",
    }
    raw = _load_json(DATA_DIR / file_map[mount_type])
    mt = raw.get("mount_type") or mount_type
    return MountSkills(
        mount_type=mt,
        slot1=_normalize(raw.get("slot1", [])),
        slot2=_normalize(raw.get("slot2", [])),
    )

def get_list(mount_type: MountType, slot: int) -> List[Skill]:
    ms = load_mount(mount_type)
    return ms.slot1 if slot == 1 else ms.slot2

def get_skill(mount_type: MountType, slot: int, index: int) -> Optional[Skill]:
    lst = get_list(mount_type, slot)
    return lst[index] if 0 <= index < len(lst) else None

def idx_prev_next(mount_type: MountType, slot: int, index: int) -> tuple[Optional[int], Optional[int]]:
    lst = get_list(mount_type, slot)
    if not lst:
        return None, None
    prev_i = index - 1 if index > 0 else None
    next_i = index + 1 if index < len(lst) - 1 else None
    return prev_i, next_i

def asset_path(rel: str) -> Path:
    """Полный путь до картинки по относительному пути из JSON."""
    return ASSETS_DIR / rel

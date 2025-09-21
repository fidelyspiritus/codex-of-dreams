# app/features/mount_skills/repo.py
from __future__ import annotations
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal, List, Dict

from app.core.config import settings
from .schemas import MountFile, Skill as SkillModel

MountType = Literal["spears", "infantry", "archers"]

@dataclass
class Skill:
    id: str
    name: str
    type: str
    description: str
    image: str

@dataclass
class MountSkills:
    mount_type: MountType
    slot1: List[Skill]
    slot2: List[Skill]

DATA_DIR = Path(getattr(settings, "MOUNT_SKILLS_DIR", Path("data") / "mount_skills"))

def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def _to_dc(s: SkillModel) -> Skill:
    return Skill(id=s.id, name=s.name, type=s.type, description=s.description, image=s.image)

@lru_cache(maxsize=3)
def load_mount(mount_type: MountType) -> MountSkills:
    file_map: Dict[MountType, str] = {
        "spears": "spears.json",
        "infantry": "infantry.json",
        "archers": "archers.json",
    }
    raw = _read(DATA_DIR / file_map[mount_type])
    mf = MountFile.model_validate(raw)  # строгая валидация структуры
    # защита от «чужого» префикса в image
    for s in mf.slot1 + mf.slot2:
        prefix = s.image.split("/", 1)[0]
        if prefix != mf.mount_type:
            raise ValueError(
                f"image mount_type mismatch: expected '{mf.mount_type}', got '{prefix}' for {s.id}"
            )
    return MountSkills(
        mount_type=mf.mount_type,
        slot1=[_to_dc(s) for s in mf.slot1],
        slot2=[_to_dc(s) for s in mf.slot2],
    )

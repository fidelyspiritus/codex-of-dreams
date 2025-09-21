# app/features/mount_skills/service.py навигация: get_list/get_skill/idx_prev_next/asset_path
from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.core.config import settings
from .repo import load_mount, Skill

ASSETS_DIR = Path(getattr(settings, "ASSETS_DIR", Path("assets"))) / "mount_skills"

def get_list(mount_type: str, slot: int) -> list[Skill]:
    ms = load_mount(mount_type)  # type: ignore[arg-type]
    return ms.slot1 if slot == 1 else ms.slot2

def get_skill(mount_type: str, slot: int, index: int) -> Optional[Skill]:
    lst = get_list(mount_type, slot)
    return lst[index] if 0 <= index < len(lst) else None

def idx_prev_next(mount_type: str, slot: int, index: int) -> tuple[Optional[int], Optional[int]]:
    lst = get_list(mount_type, slot)
    if not lst:
        return None, None
    prev_i = index - 1 if index > 0 else None
    next_i = index + 1 if index < len(lst) - 1 else None
    return prev_i, next_i

def asset_path(rel: str) -> Path:
    """Absolute path to image by relative JSON path (e.g. 'spears/hoof_strike.png')."""
    return ASSETS_DIR / rel

# app/features/admin_tools/router.py
from __future__ import annotations
from pathlib import Path
from typing import List
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.common.auth import is_admin

router = Router(name="admin_tools")

# ---- Mount skills minimal schemas ----
class MS_Skill(BaseModel):
    id: str
    name: str
    type: str
    description: str
    image: str

class MS_File(BaseModel):
    mount_type: str
    slot1: list[MS_Skill] = []
    slot2: list[MS_Skill] = []

def _list_err(title: str, issues: list[str]) -> str:
    head = f"❌ {title}:\n"
    body = "\n".join(f"• {e}" for e in issues[:80])
    tail = "\n… (truncated)" if len(issues) > 80 else ""
    return head + body + tail

# ---------- /mount_skills_check ----------
@router.message(Command("mount_skills_check"))
async def mount_skills_check(m: Message):
    if not is_admin(m.from_user.id if m.from_user else None):
        return await m.answer("🚫 Admins only.")

    data_dir = Path(settings.MOUNT_SKILLS_DIR)
    assets_dir = Path(settings.ASSETS_DIR) / "mount_skills"
    file_map = {"spears":"spears.json","infantry":"infantry.json","archers":"archers.json"}

    issues: list[str] = []
    for t, fname in file_map.items():
        p = data_dir / fname
        if not p.exists():
            issues.append(f"{fname}: file missing for '{t}'")
            continue
        try:
            mf = MS_File.model_validate_json(p.read_text(encoding="utf-8"))
        except ValidationError as ve:
            for e in ve.errors():
                loc = ".".join(str(x) for x in e["loc"])
                issues.append(f"{fname}: {loc} -> {e['msg']}")
            continue

        for slot_name in ("slot1", "slot2"):
            for s in getattr(mf, slot_name):
                prefix = s.image.split("/", 1)[0] if "/" in s.image else ""
                if prefix != mf.mount_type:
                    issues.append(f"{fname}: [{slot_name}:{s.id}] prefix '{prefix}' != '{mf.mount_type}'")
                if not (assets_dir / s.image).exists():
                    issues.append(f"{fname}: [{slot_name}:{s.id}] image missing: {assets_dir / s.image}")

        ids1 = {s.id for s in mf.slot1}
        ids2 = {s.id for s in mf.slot2}
        inter = ids1 & ids2
        if inter:
            issues.append(f"{fname}: duplicate ids across slots: {', '.join(sorted(inter))}")

    if issues:
        return await m.answer(_list_err("Mount skills issues", issues))
    return await m.answer("✅ All mount skills look good")

# ---------- /heroes_check ----------
from json import loads

@router.message(Command("heroes_check"))
async def heroes_check(m: Message):
    if not is_admin(m.from_user.id if m.from_user else None):
        return await m.answer("🚫 Admins only.")

    path = Path("data") / "heroes.json"
    if not path.exists():
        return await m.answer("❌ data/heroes.json: file missing")

    try:
        arr = loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return await m.answer(f"❌ JSON parse error: {e}")

    if not isinstance(arr, list):
        return await m.answer("❌ heroes.json must be an array")

    issues: list[str] = []
    for i, h in enumerate(arr):
        if not isinstance(h, dict):
            issues.append(f"[{i}] not an object")
            continue
        if not h.get("name"):
            issues.append(f"[{i}] missing 'name'")
        # если указан локальный image — проверим наличие файла
        img = (h.get("image") or "").strip()
        if img and "://" not in img and not Path(img).exists():
            issues.append(f"[{i}] image missing: {img}")
    if issues:
        return await m.answer(_list_err("Heroes issues", issues))
    return await m.answer("✅ Heroes look good")

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

# ---------- /events_check ----------
from json import loads

class EV_Time(BaseModel):
    duration: str | None = None
    extra_time_text: str | None = None

class EV_Rules(BaseModel):
    has_rules: bool | None = None
    rules_text: str | None = None

class EV_Entry(BaseModel):
    # минимально необходимые поля
    id: str | None = None
    name: str

    description: str | None = None
    season: str | None = None

    # могут приходить в виде списка или строки — тут не нормализуем,
    # только проверяем «что-то одно есть и тип корректный»
    rewards: list[str] | None = None
    rewards_text: str | None = None

    tips: list[str] | None = None
    tips_text: str | None = None

    bonus: str | None = None
    time: EV_Time | None = None
    rules: EV_Rules | None = None

@router.message(Command("events_check"))
async def events_check(m: Message):
    if not is_admin(m.from_user.id if m.from_user else None):
        return await m.answer("🚫 Admins only.")

    path = Path("data") / "events.json"
    if not path.exists():
        return await m.answer("❌ data/events.json: file missing")

    try:
        raw = loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return await m.answer(f"❌ JSON parse error: {e}")

    # поддерживаем и массив, и объект с ключом "events"
    if isinstance(raw, dict) and "events" in raw:
        arr = raw["events"]
    else:
        arr = raw

    if not isinstance(arr, list):
        return await m.answer("❌ events.json must be an array or an object with key 'events' (array)")

    issues: list[str] = []
    seen_ids: set[str] = set()

    for i, item in enumerate(arr):
        # базовая валидация pydantic
        try:
            ev = EV_Entry.model_validate(item)
        except ValidationError as ve:
            for e in ve.errors():
                loc = ".".join(str(x) for x in e["loc"])
                issues.append(f"[{i}] {loc} -> {e['msg']}")
            continue

        # id/name
        name = (ev.name or "").strip()
        if not name:
            issues.append(f"[{i}] empty 'name'")
        ev_id = (ev.id or "").strip()
        # id может отсутствовать — ок; но если есть, проверим на дубликаты
        if ev_id:
            if ev_id in seen_ids:
                issues.append(f"[{i}] duplicate id: {ev_id}")
            seen_ids.add(ev_id)

        # rewards/tips: допустим либо список строк, либо текст; оба — не ошибка, но предупреждение
        if ev.rewards is not None and not isinstance(ev.rewards, list):
            issues.append(f"[{i}] rewards must be a list of strings")
        if ev.tips is not None and not isinstance(ev.tips, list):
            issues.append(f"[{i}] tips must be a list of strings")

        # rules согласованность
        has_rules = (ev.rules.has_rules if ev.rules else None)
        rules_text = (ev.rules.rules_text if ev.rules else None)
        if has_rules is True and not (rules_text and rules_text.strip()):
            issues.append(f"[{i}] has_rules=true but rules_text is empty/missing")
        if has_rules is False and rules_text and rules_text.strip():
            issues.append(f"[{i}] has_rules=false but rules_text is provided")

        # time блок — просто проверим типы полей
        if ev.time is not None and not isinstance(ev.time, EV_Time):
            issues.append(f"[{i}] time must be an object with 'duration'/'extra_time_text'")

        # bonus/duration — не обязательны, но если заданы — должны быть строками
        if ev.bonus is not None and not isinstance(ev.bonus, str):
            issues.append(f"[{i}] bonus must be a string")

    if issues:
        head = "❌ Events issues:\n"
        body = "\n".join(f"• {e}" for e in issues[:100])
        tail = "\n… (truncated)" if len(issues) > 100 else ""
        return await m.answer(head + body + tail)

    return await m.answer("✅ Events look good")

# app/features/heroes/repo.py
from __future__ import annotations
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path
import re

from app.common.storage import load_json_with_fallback  

HEROES_PATHS = ("data/heroes.json", "./heroes.json")


class Talent(BaseModel):
    name: str
    type: str | None = None
    description: str | None = None


class SkillAwakening(BaseModel):
    name: str | None = None
    description: str | None = None


class HeroSkill(BaseModel):
    name: str
    type: str | None = None          # Active / Passive / Command / Counterattack, etc.
    rage: int | None = None
    level: int | None = None
    probability: str | None = None
    description: str | None = None
    awakening: SkillAwakening | None = None


class Hero(BaseModel):
    slug: str
    name: str
    season: str | None = None
    specialty: List[str] = Field(default_factory=list)
    talents: List[Talent] = Field(default_factory=list)
    skills: List[HeroSkill] = Field(default_factory=list)
    image: str | None = None   # optional explicit image path or URL


_cache: List[Hero] | None = None


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _as_list(raw: Any) -> List[dict]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("heroes"), list):
        return raw["heroes"]
    return []


def _with_image_guess(h: dict) -> dict:
    """If no image given, try data/images/<slug>.png|.jpg|.jpeg|.webp."""
    if h.get("image"):
        return h
    slug = h.get("slug") or _slugify(h.get("name", ""))
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = Path("data/images") / f"{slug}.{ext}"
        if p.exists():
            h["image"] = str(p)
            break
    return h


def _load() -> List[Hero]:
    global _cache
    if _cache is None:
        raw = load_json_with_fallback(*HEROES_PATHS)
        rows = _as_list(raw)
        normed: List[Hero] = []
        for d in rows:
            d = dict(d)
            d.setdefault("slug", _slugify(d.get("name", "")))
            d = _with_image_guess(d)
            normed.append(Hero(**d))  # pydantic приведёт вложенные dict → модели
        _cache = normed
    return _cache


def list_heroes() -> List[Hero]:
    return sorted(_load(), key=lambda h: h.name.lower())


def get_by_slug_or_name(key: str) -> Optional[Hero]:
    if not key:
        return None
    q = key.strip().lower()
    for h in _load():
        if h.slug == q or h.name.lower() == q:
            return h
    return None


def search(q: str, *, season: str | None = None, spec: str | None = None) -> List[Hero]:
    ql = (q or "").strip().lower()
    res: List[Hero] = []
    for h in _load():
        hay = " ".join([
            h.name.lower(),
            (h.season or "").lower(),
            " ".join([s.lower() for s in (h.specialty or [])]),
            " ".join([(t.name or "").lower() + " " + (t.description or "").lower() for t in (h.talents or [])]),
            " ".join([
                (sk.name or "").lower() + " " + (sk.type or "").lower() + " " + (sk.description or "").lower()
                for sk in (h.skills or [])
            ]),
        ])
        if ql and ql not in hay:
            continue
        if season and (h.season or "").lower() != season.lower():
            continue
        if spec and not any(spec.lower() in s.lower() for s in (h.specialty or [])):
            continue
        res.append(h)
    return res

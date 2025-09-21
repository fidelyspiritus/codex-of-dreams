from typing import List, Optional, Any
from pydantic import BaseModel
from .storage import load_json_with_fallback

SKILLS_PATHS = ("data/skills.json", "./skills.json")

class Skill(BaseModel):
    slug: str
    name: str
    type: str
    season: str | None = None
    probability: str | None = None
    frequency: str | None = None
    effect: str = ""
    image: str | None = None  # "data/images/..." или url


_cache: List[Skill] | None = None


def _as_list(raw: Any) -> List[dict]:
    # skills.json — это список
    if isinstance(raw, list):
        return raw
    # На всякий случай поддержим { "skills": [...] }
    if isinstance(raw, dict) and isinstance(raw.get("skills"), list):
        return raw["skills"]
    return []


def _load() -> List[Skill]:
    global _cache
    if _cache is None:
        raw = load_json_with_fallback(*SKILLS_PATHS)
        rows = _as_list(raw)
        _cache = [Skill(**x) for x in rows]
    return _cache


def list_skills() -> List[Skill]:
    return sorted(_load(), key=lambda s: s.name.lower())


def get_by_slug_or_name(key: str) -> Optional[Skill]:
    if not key:
        return None
    q = key.strip().lower()
    for s in _load():
        if s.slug == key or s.name.lower() == q:
            return s
    return None


def search(q: str, *, season: str | None = None, type_: str | None = None) -> List[Skill]:
    ql = (q or "").strip().lower()
    res = []
    for s in _load():
        if ql and ql not in (s.name.lower() + " " + s.slug.lower() + " " + (s.effect or "").lower()):
            continue
        if season and s.season != season:
            continue
        if type_ and s.type.lower() != type_.lower():
            continue
        res.append(s)
    return res

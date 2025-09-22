# app/features/skills/repo.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

from app.core.config import settings
from app.common.render import load_json

@dataclass(slots=True)
class Skill:
    slug: str
    name: str
    type: str | None = None
    season: str | None = None
    probability: str | None = None
    frequency: str | None = None
    effect: str | None = None
    image: str | None = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Skill":
        return cls(
            slug=str(d.get("slug") or d.get("id") or ""),
            name=str(d.get("name") or d.get("title") or "Skill"),
            type=d.get("type"),
            season=d.get("season"),
            probability=d.get("probability"),
            frequency=d.get("frequency"),
            effect=d.get("effect"),
            image=d.get("image"),
        )

class SkillsRepo:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self._items: List[Skill] = []
        self.reload()

    def reload(self):
        raw = load_json("skills.json", base_dir=self.data_dir)
        self._items = [Skill.from_dict(x) for x in raw]

    # basic API
    def all(self) -> List[Skill]:
        return list(self._items)

    def by_slug(self, slug: str) -> Skill | None:
        slug = (slug or "").strip().lower()
        for s in self._items:
            if s.slug.lower() == slug:
                return s
        return None

    def search(self, q: str) -> List[Skill]:
        q = (q or "").strip().lower()
        if not q:
            return self.all()
        res: List[Skill] = []
        for s in self._items:
            blob = " ".join(
                x for x in [
                    s.slug, s.name, s.type or "", s.season or "",
                    s.probability or "", s.frequency or "", s.effect or ""
                ] if x
            ).lower()
            if q in blob:
                res.append(s)
        return res

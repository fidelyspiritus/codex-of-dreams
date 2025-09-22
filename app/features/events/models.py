# app/features/events/models.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
import re

def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

class Event(BaseModel):
    id: str | None = None
    name: str
    description: str = ""
    season: str | None = None

    rewards: List[str] = Field(default_factory=list)
    rewards_text: str | None = None
    tips: List[str] = Field(default_factory=list)
    tips_text: str | None = None

    bonus: str | None = None
    duration: str | None = None
    extra_time_text: str | None = None

    has_rules: bool = False
    rules_text: str | None = None

    def model_post_init(self, __context):
        if not self.id:
            self.id = _slug(self.name)

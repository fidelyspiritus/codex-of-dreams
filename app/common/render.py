# app/common/render.py
# -*- coding: utf-8 -*-
"""
Rendering and tiny IO helpers used by features (events, skills, heroes, mounts).

This module intentionally exports stable function names expected by routers:
- load_json
- bulletize_lines, rules_block
- image_path_if_exists
- clamp_for_caption
- event_card
- render_skill
- render_hero_header, render_hero
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence, Tuple, Union, List
import json

# -----------------------------------------------------------------------------
# Settings-aware paths
# -----------------------------------------------------------------------------

try:
    from app.core.config import settings  # optional import
except Exception:
    settings = None  # pragma: no cover

# Base data dir (fallback to ./data)
DATA_DIR: Path = Path(getattr(settings, "DATA_DIR", Path("data")))

# Images dir (fallback to ./data/images)
IMAGES_DIR: Path = Path(getattr(settings, "IMAGES_DIR", DATA_DIR / "images"))

# -----------------------------------------------------------------------------
# JSON helpers
# -----------------------------------------------------------------------------

def load_json(file_name: str, base_dir: Optional[Path] = None):
    """
    Read JSON from project data directory.

    If `base_dir` is omitted, DATA_DIR is used.
    `file_name` can be either a bare name (e.g., "events.json")
    or a path relative to `base_dir`.
    """
    base = base_dir or DATA_DIR
    path = Path(file_name)
    if not path.is_absolute():
        path = base / path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------------------------------------------------------
# Text helpers
# -----------------------------------------------------------------------------

def clamp_for_caption(text: str, limit: int = 1024) -> str:
    """
    Telegram caption can be limited. Clamp gracefully with ellipsis if needed.
    """
    if text is None:
        return ""
    text = str(text)
    return text if len(text) <= limit else text[: max(0, limit - 1)].rstrip() + "…"

def _is_iterable_of_str(x: object) -> bool:
    return isinstance(x, (list, tuple)) and all(isinstance(i, str) for i in x)

def bulletize_lines(text_or_lines: Union[str, Sequence[str]], bullet: str = "• ") -> str:
    """
    Convert a multiline string or list of lines into a bullet list.
    Empty lines are ignored.
    """
    if isinstance(text_or_lines, str):
        lines = [ln.strip() for ln in text_or_lines.splitlines()]
    else:
        lines = [str(ln).strip() for ln in text_or_lines]
    lines = [ln for ln in lines if ln]
    return "\n".join(f"{bullet}{ln}" for ln in lines)

def rules_block(rules: Union[str, Sequence[str], None]) -> str:
    """
    Render rules with bullets. Returns "—" if nothing to show.
    """
    if not rules:
        return "—"
    return bulletize_lines(rules)

def _render_key_values(rows: Sequence[Tuple[str, Optional[str]]]) -> str:
    """
    Render "Key — Value" rows, skipping empty values.
    """
    out: List[str] = []
    for k, v in rows:
        if v is None:
            continue
        v = str(v).strip()
        if not v:
            continue
        out.append(f"{k} — {v}")
    return "\n".join(out)

def _normalize_source(src: Union[str, Sequence[str], None]) -> Optional[str]:
    """
    In our JSON 'source' is plain text (string or list of strings).
    We render it as plain text / bullet list (no links).
    """
    if src is None:
        return None
    if _is_iterable_of_str(src):
        return bulletize_lines(src)
    s = str(src).strip()
    return s or None

# -----------------------------------------------------------------------------
# Assets helpers
# -----------------------------------------------------------------------------

def image_path_if_exists(file_name: Optional[str],
                         images_dir: Optional[Path] = None) -> Optional[str]:
    """
    Return filesystem path to the image if it exists, otherwise None.

    - file_name may be just a base name (e.g. 'serpent.png') or a relative path.
    - images_dir defaults to IMAGES_DIR (./data/images by default).
    """
    if not file_name:
        return None
    base = images_dir or IMAGES_DIR
    path = Path(file_name)
    if not path.is_absolute():
        path = base / path
    return str(path) if path.exists() else None

# -----------------------------------------------------------------------------
# Domain renderers
# -----------------------------------------------------------------------------

def event_card(event: Mapping, show_sources: bool = True) -> str:
    """
    Human-friendly event card:

    Title
    (optional short fields like category/cycle if present)
    Rules (bulleted)
    Optional 'Source' block (plain text)
    """
    title = str(event.get("title") or event.get("name") or "Event").strip()
    header = title if title else "Event"

    # Optional short fields
    rows: List[Tuple[str, Optional[str]]] = []
    if event.get("category"):
        rows.append(("Category", str(event.get("category"))))
    if event.get("cycle"):
        rows.append(("Cycle", str(event.get("cycle"))))

    short = _render_key_values(rows)
    rules_txt = rules_block(event.get("rules") or event.get("rule"))

    parts: List[str] = [f"{header} — Rules"]
    if short:
        parts.append(short)
        parts.append("")  # blank line
    parts.append(rules_txt)

    if show_sources:
        src = _normalize_source(event.get("source"))
        if src:
            parts.append("")
            parts.append("Source")
            parts.append(src)

    return "\n".join(parts).strip()

def render_skill(skill: Mapping) -> str:
    """
    Text-only skill representation (used as caption).
    Understands common keys from skills.json:
    slug, name/title, type, season, probability, frequency, effect.
    """
    name = str(skill.get("name") or skill.get("title") or "Skill").strip()
    rows = [
        ("Type",        skill.get("type")),
        ("Season",      skill.get("season")),
        ("Probability", skill.get("probability")),
        ("Frequency",   skill.get("frequency")),
    ]
    head = name
    body = _render_key_values(rows)
    effect = str(skill.get("effect") or "").strip()

    parts: List[str] = [head]
    if body:
        parts.append(body)
    if effect:
        parts.append("")
        parts.append(effect)

    return "\n".join(parts).strip()

def render_hero_header(hero: Mapping) -> str:
    """
    Compact hero header line used in list or at the top of the hero card.
    """
    name = str(hero.get("name") or hero.get("title") or "Hero").strip()
    clazz = str(hero.get("class") or hero.get("type") or "").strip()
    role  = str(hero.get("role") or "").strip()

    tags = " · ".join(x for x in (clazz, role) if x)
    return f"{name}" if not tags else f"{name} — {tags}"

def render_hero(hero: Mapping) -> str:
    """
    Full hero card (text). Keeps it resilient to missing fields.
    """
    rows = [
        ("Rarity",  hero.get("rarity")),
        ("Faction", hero.get("faction")),
        ("Role",    hero.get("role")),
    ]
    head = render_hero_header(hero)
    body = _render_key_values(rows)
    desc = str(hero.get("description") or "").strip()

    parts: List[str] = [head]
    if body:
        parts.append(body)
    if desc:
        parts.append("")
        parts.append(desc)

    return "\n".join(parts).strip()

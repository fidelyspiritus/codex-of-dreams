import html
from typing import Iterable
import textwrap
import json
from pathlib import Path

def esc(s: str | None) -> str:
    return html.escape(s or "")

# =========================
# Common helpers
# =========================
def bullets(items: Iterable[str] | None) -> str:
    """
    Render list as bullet points.
    If items is empty/None -> return empty string (no placeholder dashes).
    """
    if not items:
        return ""
    return "\n".join(f"• {esc(x)}" for x in items)

def _join_nonempty_lines(parts: list[str]) -> str:
    """Join non-empty lines, collapsing multiple blank lines."""
    out: list[str] = []
    for p in parts:
        p = (p or "").rstrip()
        if not p:
            # avoid multiple consecutive blank lines
            if out and out[-1] == "":
                continue
            out.append("")
        else:
            out.append(p)
    # trim trailing empties
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)

def _join_nonempty(*parts: str) -> str:
    return " ".join([p for p in parts if p])

def clamp_for_caption(text: str, limit: int = 1000) -> str:
    if len(text) <= limit:
        return text
    return textwrap.shorten(text, width=limit, placeholder="…")

# =========================
# Events
# =========================
def event_card(ev) -> str:
    """
    Expect normalized Event model:
    name, description, rewards(list[str])|rewards_text, tips(list[str])|tips_text,
    bonus(str), duration(str), extra_time_text(str)|None, has_rules(bool)
    """
    name = esc(ev.name)
    desc = esc(ev.description or "")

    rewards_block = (
        bullets(ev.rewards)
        if getattr(ev, "rewards", None) is not None
        else esc(getattr(ev, "rewards_text", "") or "")
    )
    tips_block = (
        bullets(ev.tips)
        if getattr(ev, "tips", None) is not None
        else esc(getattr(ev, "tips_text", "") or "")
    )

    bonus = esc(ev.bonus or "")            # no "—", no "None" if empty
    duration = esc(ev.duration or "")

    parts: list[str] = [f"<b>{name}</b>", ""]

    # Description
    if desc:
        parts += ["<b>• Description:</b>", desc, ""]

    # Rewards
    if rewards_block:
        parts += ["<b>• Rewards:</b>", rewards_block, ""]

    # Bonus (only if present)
    if bonus:
        parts.append(f"✨ <b>Bonus:</b> {bonus}")
        parts.append("")

    # Tips
    if tips_block:
        parts += ["<b>• Tips:</b>", tips_block, ""]

    # Time (only if duration/extra text provided)
    time_lines = []
    if duration:
        time_lines.append(f"Duration: {duration}")
    if getattr(ev, "extra_time_text", None):
        time_lines.append(esc(ev.extra_time_text))
    if time_lines:
        parts += ["<b>• Time:</b>", "\n".join(time_lines)]

    return _join_nonempty_lines(parts)

def rules_block(title: str, rules_text: str) -> str:
    body = esc(rules_text or "")
    if not body:
        # If there are no rules, show title only
        return f"<b>{esc(title)} — Rules</b>"
    return f"<b>{esc(title)} — Rules</b>\n\n{body}"

# =========================
# Skills
# =========================
def skill_card(s) -> str:
    """
    s — Skill object from skills_repo
    """
    parts: list[str] = [f"<b>{esc(s.name)}</b>"]

    # Type / Season in one line (only what exists)
    type_season = []
    if s.type:
        type_season.append(f"Type: {esc(s.type)}")
    if s.season:
        type_season.append(f"Season: {esc(s.season)}")
    if type_season:
        parts.append("   ".join(type_season))
        parts.append("")

    # Effect
    if s.effect:
        parts += ["<b>• Effect:</b>", esc(s.effect), ""]

    # Probability / Frequency
    if s.probability:
        parts.append(f"Probability: {esc(s.probability)}")
    if s.frequency:
        parts.append(f"Frequency: {esc(s.frequency)}")

    return _join_nonempty_lines(parts)

# =========================
# Heroes (styled)
# =========================
def hero_header(h) -> str:
    """
    Compact header for caption (<= ~1000 chars).
    """
    lines = [f"<b>Hero:</b> {esc(h.name)}"]
    if h.season:
        lines.append(f"<b>Season:</b> {esc(h.season)}")
    if getattr(h, "specialty", None):
        spec = ", ".join(esc(x) for x in h.specialty if x)
        if spec:
            lines.append(f"<b>Specialty:</b> {spec}")
    return "\n".join(lines)

def _skill_line_numbered(i: int, sk) -> str:
    """
    1. Flame Slash (Active, Rage 1000, Lv.10)
       • Deals ...
       • Awakening — Desperate Strike (Rage 1000, Lv.1): ...
    """
    badges = []
    if sk.type:
        badges.append(esc(sk.type))
    if sk.rage is not None:
        badges.append(f"Rage {sk.rage}")
    if sk.level is not None:
        badges.append(f"Lv.{sk.level}")
    if sk.probability:
        badges.append(f"Probability {esc(sk.probability)}")
    meta = f" ({', '.join(badges)})" if badges else ""
    head = f"{i}. <b>{esc(sk.name)}</b>{meta}"

    body = ""
    if sk.description:
        body = f"• {esc(sk.description)}"
    if getattr(sk, "awakening", None) and (sk.awakening.name or sk.awakening.description):
        aw_name = esc(sk.awakening.name or "Awakening")
        aw_desc = esc(sk.awakening.description or "")
        line = f"• <i>Awakening — {aw_name}</i>"
        if aw_desc:
            line += f": {aw_desc}"
        body = f"{body}\n{line}" if body else line
    return f"{head}\n{body}" if body else head

def hero_card(h) -> str:
    """
    Full hero card:
    - Header with labels
    - 'Talents' as bullets (only if present)
    - 'Skills' as numbered list (only if present)
    """
    parts: list[str] = [hero_header(h)]

    # divider (single, not repeated)
    parts += [ "──────────"]

    # Talents
    talents_lines: list[str] = []
    if getattr(h, "talents", None):
        for t in h.talents:
            if not (t and (t.name or t.description or t.type)):
                continue
            line = f"• <b>{esc(t.name)}</b>" if t.name else "•"
            if t.type:
                line += f" (<i>{esc(t.type)}</i>)"
            if t.description:
                line += f": {esc(t.description)}"
            talents_lines.append(line)
    if talents_lines:
        parts += ["<b>Talents</b>", "\n".join(talents_lines), ""]

    # Skills
    skill_lines: list[str] = []
    if getattr(h, "skills", None):
        for idx, sk in enumerate(h.skills, start=1):
            line = _skill_line_numbered(idx, sk)
            if line:
                skill_lines.append(line)
    if skill_lines: 
        parts += ["<b>Skills</b>", "\n".join(skill_lines)]

    return _join_nonempty_lines(parts)

def load_json(file_path: Path):
    """Load JSON data from file, return list or empty list."""
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
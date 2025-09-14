import html
from typing import Iterable

def esc(s: str | None) -> str:
    return html.escape(s or "")

def bullets(items: Iterable[str] | None) -> str:
    if not items:
        return "—"
    return "\n".join(f"• {esc(x)}" for x in items)

def event_card(ev) -> str:
    """
    Ожидаем нормализованную модель Event:
    name, description, rewards(list[str])|rewards_text, tips(list[str])|tips_text,
    bonus(str), duration(str), extra_time_text(str)|None, has_rules(bool)
    """
    name = esc(ev.name)
    desc = esc(ev.description)
    rewards_block = bullets(ev.rewards) if ev.rewards is not None else (esc(ev.rewards_text or "—"))
    tips_block = bullets(ev.tips) if ev.tips is not None else (esc(ev.tips_text or "—"))
    bonus = esc(ev.bonus or "None")
    duration = esc(ev.duration or "—")

    parts = [
        f"<b>{name}</b>",
        "",
        "<b>• Description:</b>",
        desc or "—",
        "",
        "<b>• Rewards:</b>",
        rewards_block,
        f"✨ <b>Bonus:</b> {bonus}",
        "",
        "<b>• Tips:</b>",
        tips_block,
        "",
        "<b>• Time:</b>",
        f"Duration: {duration}",
    ]
    if ev.extra_time_text:
        parts.append(esc(ev.extra_time_text))
    return "\n".join(parts)

def rules_block(title: str, rules_text: str) -> str:
    return f"<b>{esc(title)} — Rules</b>\n\n{esc(rules_text or '—')}"

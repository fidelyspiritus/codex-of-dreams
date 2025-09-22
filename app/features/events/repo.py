# app/features/events/repo.py
from typing import List, Optional, Any
from .models import Event
from app.common.storage import load_json_with_fallback  # ← фикс импорта

# Основной путь → data/events.json; запасной → ./events.json
EVENTS_PATHS = ("data/events.json", "./events.json")

_cache: List[Event] | None = None


def _as_list(raw: Any) -> List[dict]:
    # Поддерживаем твой формат с корневым ключом "events" (или список)
    if isinstance(raw, dict) and isinstance(raw.get("events"), list):
        return raw["events"]
    if isinstance(raw, list):
        return raw
    # Ещё вариант — один объект под "event"
    if isinstance(raw, dict) and isinstance(raw.get("event"), dict):
        return [raw["event"]]
    return []


def _norm_event(d: dict) -> dict:
    """
    Нормализуем поля к Event:
    - time.duration → duration
    - rewards(dict|list[dict]|list[str]) → list[str] / rewards_text
    - bonus(dict) → строка
    - rules(list[str]) → rules_text + has_rules
    - source(list[str]) → склеим в tips_text (если tips не заполнен)
    """
    out = dict(d)

    # time → duration (+ при желании можно собрать окно)
    t = d.get("time")
    if isinstance(t, dict):
        if t.get("duration"):
            out["duration"] = t.get("duration")
        # window = t.get("window")
        # if window and not out.get("extra_time_text"):
        #     out["extra_time_text"] = f"Window: {window}"

    # rewards: dict → list[str]; list[dict] → list[str]
    rw = d.get("rewards")
    if isinstance(rw, dict):
        name = rw.get("name") or ""
        notes = " — ".join([x for x in [rw.get("rarity"), rw.get("notes")] if x])
        out["rewards"] = [f"{name}" + (f" — {notes}" if notes else "")]
        out.pop("rewards_text", None)
    elif isinstance(rw, list) and rw and isinstance(rw[0], dict):
        out["rewards"] = [
            (" — ".join([v for v in [x.get("name") or x.get("rarity"), x.get("notes")] if v])
             or (x.get("name") or x.get("rarity") or ""))
            for x in rw
        ]

    # bonus: dict → строка
    bn = d.get("bonus")
    if isinstance(bn, dict):
        parts = [bn.get("type"), bn.get("value"), bn.get("scope"), bn.get("notes")]
        out["bonus"] = " | ".join([p for p in parts if p])

    # rules: list[str] → rules_text + has_rules
    rules = d.get("rules")
    if isinstance(rules, list) and rules and isinstance(rules[0], str):
        out["rules_text"] = "\n".join(rules)
        out["has_rules"] = True

    # source: list[str] → если tips пустой — используем как tips_text
    src = d.get("source")
    if (not out.get("tips")) and (not out.get("tips_text")) and isinstance(src, list):
        out["tips_text"] = "\n".join(src)

    return out


def _load() -> List[Event]:
    global _cache
    if _cache is None:
        raw = load_json_with_fallback(*EVENTS_PATHS)
        items = _as_list(raw)
        normed = [_norm_event(x) for x in items]
        _cache = [Event(**x) for x in normed]
    return _cache


def list_events() -> List[Event]:
    return sorted(_load(), key=lambda e: e.name.lower())


def get_by_name(name: str) -> Optional[Event]:
    if not name:
        return None
    q = name.strip().lower()
    for ev in _load():
        if ev.name.lower() == q:
            return ev
    return None


def get_by_id(ev_id: str) -> Optional[Event]:
    for ev in _load():
        if ev.id == ev_id:
            return ev
    return None


def search(q: str) -> List[Event]:
    ql = (q or "").strip().lower()
    if not ql:
        return []
    res = []
    for e in _load():
        hay = " ".join([
            e.name.lower(),
            e.description.lower(),
            " ".join(e.rewards or []),
            " ".join(e.tips or []),
            (e.rewards_text or "").lower(),
            (e.tips_text or "").lower(),
            (e.bonus or "").lower(),
            (e.duration or "").lower(),
            (e.extra_time_text or "").lower(),
            (e.rules_text or "").lower(),
            (e.season or "").lower(),
        ])
        if ql in hay:
            res.append(e)
    return res

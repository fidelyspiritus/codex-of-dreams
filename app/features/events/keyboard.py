# app/features/events/keyboard.py
from __future__ import annotations
from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.common.callbacks import EventCb

PER_PAGE = 10

def kb_events(names: List[str], page: int = 0) -> InlineKeyboardMarkup:
    start = max(page, 0) * PER_PAGE
    chunk = names[start:start + PER_PAGE]

    rows: list[list[InlineKeyboardButton]] = []
    for name in chunk:
        cb = EventCb(action="view", id=name)   # id = имя события (repo поддерживает поиск по name/id)
        rows.append([InlineKeyboardButton(text=name, callback_data=cb.pack())])

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="⭠ Prev",
            callback_data=EventCb(action="page", page=page-1).pack()
        ))
    if start + PER_PAGE < len(names):
        nav.append(InlineKeyboardButton(
            text="Next ⭢",
            callback_data=EventCb(action="page", page=page+1).pack()
        ))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_event_details(ev_id: str, has_rules: bool) -> InlineKeyboardMarkup | None:
    if not has_rules:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📜 Rules",
                callback_data=EventCb(action="rules", id=ev_id).pack()
            )
        ]]
    )

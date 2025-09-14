from typing import Iterable
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B
from app.utils.callbacks import EventCb

def events_list(names: Iterable[str], page: int = 0, per: int = 10) -> InlineKeyboardMarkup:
    names = list(names)
    start = page * per
    chunk = names[start:start+per]
    rows = [[B(text=n, callback_data=EventCb(action="view", id=n).pack())] for n in chunk]

    nav = []
    if page > 0:
        nav.append(B(text="⭠", callback_data=EventCb(action="page", page=page-1).pack()))
    if start + per < len(names):
        nav.append(B(text="⭢", callback_data=EventCb(action="page", page=page+1).pack()))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def details_kb(ev_id: str, has_rules: bool):
    rows = []
    if has_rules:
        rows.append([B(text="📜 Rules", callback_data=EventCb(action="rules", id=ev_id).pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

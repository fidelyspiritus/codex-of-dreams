# app/features/skills/keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Sequence

def list_kb(items: Sequence[tuple[str, str]], cb_prefix: str = "skills:view:") -> InlineKeyboardMarkup:
    """
    items: sequence of (slug, title)
    """
    rows = []
    for slug, title in items:
        rows.append([InlineKeyboardButton(text=title, callback_data=f"{cb_prefix}{slug}")])
    return InlineKeyboardMarkup(inline_keyboard=rows or [[
        InlineKeyboardButton(text="No results", callback_data="noop")
    ]])

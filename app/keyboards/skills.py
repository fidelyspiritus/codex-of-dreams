from typing import Iterable
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B

def skills_list(names: Iterable[str], per: int = 10) -> InlineKeyboardMarkup:
    # Для простоты без пагинации: компактный список
    rows = [[B(text=n, callback_data=f"skill:{n}") ] for n in names]
    return InlineKeyboardMarkup(inline_keyboard=rows)

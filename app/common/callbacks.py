# app/common/callbacks.py
from __future__ import annotations
from typing import Literal
from aiogram.filters.callback_data import CallbackData

Action = Literal["view", "rules", "page"]

class EventCb(CallbackData, prefix="ev"):
    action: Action
    id: str = ""
    page: int = 0

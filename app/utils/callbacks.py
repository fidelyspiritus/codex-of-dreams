from aiogram.filters.callback_data import CallbackData

class EventCb(CallbackData, prefix="ev"):
    action: str   # view / rules / page
    id: str = ""
    page: int = 0

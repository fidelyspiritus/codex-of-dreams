from aiogram import Router
from aiogram.types import ErrorEvent
router = Router()

@router.errors()
async def on_error(e: ErrorEvent):
    try:
        await e.update.callback_query.answer("Something went wrong.", show_alert=True)
    except Exception:
        pass

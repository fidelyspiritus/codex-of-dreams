from aiogram import Router, types
from aiogram.filters import Command
router = Router()

HELP = (
    "🧰 <b>Commands</b>\n"
    "/events — list all events\n"
    "/event &lt;name&gt; — event details by name\n"
    "/search_em &lt;word&gt; — search events\n"
    "/help — this message"
)

@router.message(Command("start", "help"))
async def cmd_help(m: types.Message):
    await m.answer(HELP)

from pathlib import Path
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile,
)

router = Router()

WELCOME_TEXT = (
    "👋 Hello, <b>{name}</b>!\n\n"
    "Welcome to <b>Codex of Dreams</b>.\n"
    "You can quickly check:\n"
    "• <b>/events</b> – list or search events\n"
    "• <b>/skills</b> – list or search skills\n\n"
    "Type a command or use buttons below 👇"
)

HELP_TEXT = (
    "📖 <b>Commands</b>\n\n"
    "/events – show events (list or search)\n"
    "/skills – show skills (list or search)\n"
)

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/events"), KeyboardButton(text="/skills")],
        ],
        resize_keyboard=True,
    )

def quick_links_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Events", callback_data="menu:events"),
                InlineKeyboardButton(text="🧠 Skills", callback_data="menu:skills"),
            ]
        ]
    )

def _find_banner() -> Path | None:
    for name in ["banner.png", "banner.jpg", "welcome.png", "welcome.jpg"]:
        p = Path("data/images") / name
        if p.exists():
            return p
    return None

@router.message(CommandStart())
async def cmd_start(m: types.Message):
    name = m.from_user.first_name or "friend"
    banner = _find_banner()

    if banner:
        await m.answer_photo(
            photo=FSInputFile(banner),
            caption=WELCOME_TEXT.format(name=name),
            reply_markup=quick_links_inline(),
        )
    else:
        await m.answer(
            WELCOME_TEXT.format(name=name),
            reply_markup=quick_links_inline(),
        )
    await m.answer("Choose command:", reply_markup=main_menu_keyboard())

@router.message(Command("help"))
async def cmd_help(m: types.Message):
    await m.answer(HELP_TEXT, reply_markup=main_menu_keyboard())

@router.callback_query(lambda c: c.data in {"menu:events", "menu:skills"})
async def cb_menu_open(q: types.CallbackQuery):
    await q.message.answer("/events" if q.data == "menu:events" else "/skills")
    await q.answer()

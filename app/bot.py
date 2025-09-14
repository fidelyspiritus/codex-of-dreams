from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

def build_bot(token: str) -> Bot:
    return Bot(
        token=token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            # disable_web_page_preview=True,
            # protect_content=True,
        ),
    )

def build_dispatcher() -> Dispatcher:
    return Dispatcher()

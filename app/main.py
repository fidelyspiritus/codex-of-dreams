# app/main.py
import asyncio
import logging
from aiogram import types
from aiogram.types import BotCommand

from app.bot import build_bot, build_dispatcher
from app.config import settings
from app.handlers import base, events, errors, skills, heroes


async def set_commands(bot):
    """Single, clean command set (applies to default scope)."""
    cmds = [
        BotCommand(command="help",   description="Help & commands"),
        BotCommand(command="events", description="Events (list/search)"),
        BotCommand(command="skills", description="Skills (list/search)"),
        BotCommand(command="heroes", description="Heroes (list/search)"),
    ]
    await bot.set_my_commands(cmds)  # default scope is enough in most cases


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    bot = build_bot(settings.BOT_TOKEN)
    dp = build_dispatcher()

    # Wire routers
    dp.include_router(base.router)
    dp.include_router(events.router)
    dp.include_router(skills.router)
    dp.include_router(heroes.router)
    dp.include_router(errors.router)

    # Commands & startup info
    await set_commands(bot)
    me = await bot.get_me()
    logging.info("✅ Bot started as @%s (id=%s)", me.username, me.id)

    # Start polling (will exit on KeyboardInterrupt)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Graceful stop on Ctrl+C / termination
        print("🛑 Bot stopped")

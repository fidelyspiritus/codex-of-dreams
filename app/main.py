import asyncio
import logging
from aiogram.types import BotCommand
from app.bot import build_bot, build_dispatcher
from app.config import settings
from app.handlers import base, events, errors, skills

async def set_commands(bot):
    cmds = [
        BotCommand(command="help", description="help"),
        BotCommand(command="events", description="Events (list/search)"),
    ]
    # Добавим команды для skills только если модуль есть
    if skills is not None:
        cmds += [
            BotCommand(command="skills", description="Skills (list/search)"),
        ]
    await bot.set_my_commands(cmds)

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    bot = build_bot(settings.BOT_TOKEN)
    dp = build_dispatcher()

    dp.include_router(base.router)
    dp.include_router(events.router)
    dp.include_router(skills.router)
    dp.include_router(errors.router)

    await set_commands(bot)
    me = await bot.get_me()
    print(f"✅ Bot started as @{me.username} (id={me.id})")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
from aiogram import types
from aiogram.types import BotCommand

from app.core.bot import build_bot, build_dispatcher
from app.core.config import settings
from app.features.errors import errors
from app.features.events import router as event_router
from app.features.heroes import router as heroes_router
from app.features.skills import router as skills_router
from app.features.mount_skills import router as mount_skills_router
from app.features.equipment import router as equipment_router
from app.features.jewels import router as jewels_router
from app.features.kvk import router as kvk_router
from app.features.base import base
from app.features.admin_tools import router as admin_tools_router  # <- новый импорт


async def set_commands_all(bot):
    cmds = [
        types.BotCommand(command="help",         description="Help & commands"),
        types.BotCommand(command="events",       description="Events (list/search)"),
        types.BotCommand(command="skills",       description="Skills (list/search)"),
        types.BotCommand(command="heroes",       description="Heroes (list/search)"),
        types.BotCommand(command="kvk3",         description="KvK - 3 (WIP)"),
        types.BotCommand(command="mount_skills", description="Mount skills (WIP)"),
        types.BotCommand(command="equipment",    description="Equipment (WIP)"),
        types.BotCommand(command="jewels",       description="Jewels (WIP)"),
    ]
    await bot.delete_my_commands(scope=types.BotCommandScopeDefault())
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.delete_my_commands(scope=types.BotCommandScopeAllGroupChats())
    await bot.delete_my_commands(scope=types.BotCommandScopeAllChatAdministrators())
    await bot.set_my_commands(cmds, scope=types.BotCommandScopeDefault())
    await bot.set_my_commands(cmds, scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(cmds, scope=types.BotCommandScopeAllGroupChats())
    await bot.set_my_commands(cmds, scope=types.BotCommandScopeAllChatAdministrators())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    bot = build_bot(settings.BOT_TOKEN)
    dp = build_dispatcher()

    # Подключаем все роутеры
    dp.include_router(base.router)
    dp.include_router(event_router.router)
    dp.include_router(heroes_router.router)
    dp.include_router(skills_router.router)
    dp.include_router(mount_skills_router.router)
    dp.include_router(equipment_router.router) 
    dp.include_router(jewels_router.router)
    dp.include_router(kvk_router.router) 
 
     # ← только когда флаг включён
    if settings.ENABLE_ADMIN_TOOLS:
        dp.include_router(admin_tools_router.router)

    dp.include_router(errors.router)

    # Команды и стартовая инфа
    await set_commands_all(bot)
    me = await bot.get_me()
    logging.info("✅ Bot started as @%s (id=%s)", me.username, me.id)

    # Запуск long-polling (завершается по Ctrl+C)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped")

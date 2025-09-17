from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from pathlib import Path
from app.utils.render import load_json

router = Router()
MOUNTS_FILE = Path("data/mount_skills.json")

@router.message(Command("mount_skills"))
async def cmd_mounts(message: Message):
    mounts = load_json(MOUNTS_FILE)
    if not mounts:
        await message.answer("🦄 Mounts section is under development.")
        return
    # тут будет логика вывода, когда данные появятся
    text = "\n".join([m["name"] for m in mounts])
    await message.answer(f"🦄 Mounts:\n{text}")

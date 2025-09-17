from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from pathlib import Path
from app.utils.render import load_json

router = Router()
KVK_FILE = Path("data/kvk.json")

@router.message(Command("kvk3"))
async def cmd_kvk(message: Message):
    kvk = load_json(KVK_FILE)
    if not kvk:
        await message.answer("⚔️ KvK-3 section is under development.")
        return
    text = "\n".join([k.get("name", "Unknown") for k in kvk])
    await message.answer(f"⚔️ KvK-3:\n{text}")

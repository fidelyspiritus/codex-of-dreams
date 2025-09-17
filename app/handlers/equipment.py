from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from pathlib import Path
from app.utils.render import load_json

router = Router()
EQUIPMENT_FILE = Path("data/equipment.json")

@router.message(Command("equipment"))
async def cmd_equipment(message: Message):
    equipment = load_json(EQUIPMENT_FILE)
    if not equipment:
        await message.answer("🛡️ Equipment section is under development.")
        return
    text = "\n".join([e.get("name", "Unknown") for e in equipment])
    await message.answer(f"🛡️ Equipment:\n{text}")

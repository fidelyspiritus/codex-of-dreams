from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda msg: msg.text and msg.text.lower().startswith("/jewels"))
async def jewels_handler(message: Message):
    await message.answer("💎 Jewels section is under development...")

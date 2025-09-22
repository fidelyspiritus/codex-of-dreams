# app/features/skills/router.py
from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import Command

from app.common.render import load_json, render_skill, image_path_if_exists  # NEW
from app.core.config import settings

router = Router(name=__name__)

@router.message(Command("skills"))
async def skills_entry(message: types.Message):
    """
    /skills — список всех или поиск:
      /skills <text>
    """
    query = message.text.split(maxsplit=1)
    needle = query[1].strip().lower() if len(query) > 1 else ""

    skills = load_json("skills.json", base_dir=settings.DATA_DIR)

    # skills.json может быть {"skills":[...]} или просто списком
    if isinstance(skills, dict):
        skills = skills.get("skills", [])

    if needle:
        skills = [
            s for s in skills
            if needle in str(s.get("name", "")).lower()
            or needle in str(s.get("effect", "")).lower()
        ]

    if not skills:
        await message.answer("No skills found.")
        return

    # отправляем по одному: если есть картинка — с фото, иначе текстом
    sent = 0
    for s in skills:
        caption = render_skill(s)
        img = image_path_if_exists(settings.DATA_DIR, s.get("image"))
        if img:
            await message.answer_photo(types.FSInputFile(img), caption=caption)
        else:
            await message.answer(caption)
        sent += 1
        if sent >= 10:  # чтобы не заспамить, ограничим пачку
            break

# app/features/mount_skills/router.py экраны: меню → слоты → список → карточка + prev/next
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command

from app.features.mount_skills import service as S
from app.features.mount_skills.keyboard import type_menu_kb, slots_kb, list_kb, item_kb, empty_list_kb

from app.common.auth import is_admin
from app.features.mount_skills.schemas import MountFile, MountType
from app.core.config import settings
from pathlib import Path
from pydantic import ValidationError

router = Router(name="mount_skills")

def _caption(skill, index: int | None = None, total: int | None = None) -> str:
    pos = f" ({index+1}/{total})" if index is not None and total is not None else ""
    return f"<b>{skill.name}</b>{pos}\n<i>Type:</i> {skill.type}\n\n{skill.description}"

@router.message(Command("mount_skills"))
async def cmd_mount_skills(message: Message):
    await message.answer("Choose mount type:", reply_markup=type_menu_kb())

@router.callback_query(F.data == "ms:menu")
async def cb_menu(c: CallbackQuery):
    await c.message.edit_text("Choose mount type:", reply_markup=type_menu_kb())
    await c.answer()

@router.callback_query(F.data.startswith("ms:slots:"))
async def cb_slots(c: CallbackQuery):
    _, _, t = c.data.split(":")
    await c.message.edit_text(f"{t.title()} — Slots", reply_markup=slots_kb(t))
    await c.answer()

@router.callback_query(F.data.startswith("ms:list:"))
async def cb_list(c: CallbackQuery):
    _, _, t, s = c.data.split(":")
    s = int(s)
    skills = S.get_list(t, s)
    names = [x.name for x in skills]
    if not names:
        await c.message.edit_text(
            f"{t.title()} — Slot {s}\n\nNo skills yet.",
            reply_markup=empty_list_kb(t, s)
        )
    else:
        await c.message.edit_text(
            f"{t.title()} — Slot {s}\nPick a skill:",
            reply_markup=list_kb(t, s, names)
        )
    await c.answer()

@router.callback_query(F.data.startswith("ms:item:"))
async def cb_item(c: CallbackQuery):
    _, _, t, s, i = c.data.split(":")
    s, i = int(s), int(i)
    skills = S.get_list(t, s)
    skill = S.get_skill(t, s, i)
    if not skill:
        await c.answer("Skill not found", show_alert=True)
        return

    prev_i, next_i = S.idx_prev_next(t, s, i)
    kb = item_kb(t, s, i, prev_i, next_i)
    caption = _caption(skill, i, len(skills))
    photo_path = S.asset_path(skill.image)

    try:
        photo = FSInputFile(photo_path)
        try:
            await c.message.delete()
        except Exception:
            pass
        await c.message.answer_photo(photo=photo, caption=caption, reply_markup=kb, parse_mode="HTML")
    except Exception:
        try:
            await c.message.delete()
        except Exception:
            pass
        await c.message.answer(caption + f"\n\n<i>(image not found: {skill.image})</i>", reply_markup=kb, parse_mode="HTML")
    await c.answer()

@router.callback_query(F.data.startswith("ms:nav:"))
async def cb_nav(c: CallbackQuery):
    _, _, t, s, i, action = c.data.split(":")
    s, i = int(s), int(i)
    i = i - 1 if action == "prev" else i + 1

    skills = S.get_list(t, s)
    skill = S.get_skill(t, s, i)
    if not skill:
        await c.answer("No more items")
        return

    prev_i, next_i = S.idx_prev_next(t, s, i)
    kb = item_kb(t, s, i, prev_i, next_i)
    caption = _caption(skill, i, len(skills))
    photo_path = S.asset_path(skill.image)

    try:
        media = InputMediaPhoto(media=FSInputFile(photo_path), caption=caption, parse_mode="HTML")
        await c.message.edit_media(media=media, reply_markup=kb)
    except Exception:
        try:
            await c.message.edit_text(caption + f"\n\n<i>(image not found: {skill.image})</i>", reply_markup=kb, parse_mode="HTML")
        except Exception:
            await c.message.answer(caption + f"\n\n<i>(image not found: {skill.image})</i>", reply_markup=kb, parse_mode="HTML")
    await c.answer()

@router.message(Command("mount_skills_check"))
async def cmd_mount_skills_check(message: Message):
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return await message.reply("🚫 Admins only.")

    data_dir = Path(settings.MOUNT_SKILLS_DIR)
    assets_dir = Path(settings.ASSETS_DIR) / "mount_skills"
    file_map: dict[str, str] = {"spears":"spears.json","infantry":"infantry.json","archers":"archers.json"}

    issues: list[str] = []
    for t, fname in file_map.items():
        p = data_dir / fname
        if not p.exists():
            issues.append(f"{fname}: file missing for '{t}'")
            continue
        try:
            mf = MountFile.model_validate_json(p.read_text(encoding="utf-8"))
        except ValidationError as ve:
            for err in ve.errors():
                loc = ".".join(str(x) for x in err["loc"])
                issues.append(f"{fname}: {loc} -> {err['msg']}")
            continue
        # лёгкие доменные проверки
        for slot_name in ("slot1","slot2"):
            slot = getattr(mf, slot_name)
            for s in slot:
                prefix = s.image.split("/",1)[0]
                if prefix != mf.mount_type:
                    issues.append(f"{fname}: [{slot_name}:{s.id}] prefix '{prefix}' != '{mf.mount_type}'")
                img_path = assets_dir / s.image
                if not img_path.exists():
                    issues.append(f"{fname}: [{slot_name}:{s.id}] image missing: {img_path}")

        ids1 = {s.id for s in mf.slot1}; ids2 = {s.id for s in mf.slot2}
        inter = ids1 & ids2
        if inter:
            issues.append(f"{fname}: duplicate ids across slots: {', '.join(sorted(inter))}")

    if issues:
        text = "❌ Mount skills issues:\n" + "\n".join(f"• {e}" for e in issues[:50])
    else:
        text = "✅ All mount skills look good."
    await message.reply(text)
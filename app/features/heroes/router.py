# app/features/heroes/router.py
from pathlib import Path
from typing import List, Tuple
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from . import repo
from app.common.render import hero_header, hero_card, clamp_for_caption

router = Router()
PER_PAGE = 10


def _pairs_all() -> List[Tuple[str, str]]:
    return [(h.name, h.slug) for h in repo.list_heroes()]

def _kb_heroes(pairs: List[Tuple[str, str]], page: int = 0) -> InlineKeyboardMarkup:
    start = page * PER_PAGE
    chunk = pairs[start:start + PER_PAGE]
    rows = [[InlineKeyboardButton(text=name, callback_data=f"hr:view:{slug}")]
            for name, slug in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⭠ Prev", callback_data=f"hr:list:{page - 1}"))
    if start + PER_PAGE < len(pairs):
        nav.append(InlineKeyboardButton(text="Next ⭢", callback_data=f"hr:list:{page + 1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)

async def _send_hero(message: types.Message, h) -> None:
    header = clamp_for_caption(hero_header(h))
    full = hero_card(h)
    img = (h.image or "").strip()
    if img:
        p = Path(img)
        if p.exists() and p.is_file():
            await message.answer_photo(photo=FSInputFile(p), caption=header)
            if len(full) > len(header):
                await message.answer(full)
            return
        if img.startswith("http://") or img.startswith("https://"):
            await message.answer_photo(photo=img, caption=header)
            if len(full) > len(header):
                await message.answer(full)
            return
    await message.answer(full)

@router.message(Command("heroes"))
async def cmd_heroes(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) == 1:
        pairs = _pairs_all()
        if not pairs:
            return await m.answer("No heroes yet.")
        return await m.answer("Select a hero:", reply_markup=_kb_heroes(pairs, page=0))
    q = parts[1].strip()
    hits = repo.search(q)
    if not hits:
        return await m.answer("No matches found.")
    pairs = [(h.name, h.slug) for h in hits][:30]
    await m.answer(f"Found {len(hits)} match(es). Select:", reply_markup=_kb_heroes(pairs, page=0))

@router.callback_query(F.data.startswith("hr:list:"))
async def cb_list(q: types.CallbackQuery):
    try:
        page = int(q.data.split(":", 2)[2])
    except Exception:
        page = 0
    pairs = _pairs_all()
    await q.message.edit_reply_markup(reply_markup=_kb_heroes(pairs, page=page))
    await q.answer()

@router.callback_query(F.data.startswith("hr:view:"))
async def cb_view(q: types.CallbackQuery):
    slug = q.data.split(":", 2)[2]
    h = repo.get_by_slug_or_name(slug)
    if not h:
        return await q.answer("Not found", show_alert=True)
    await _send_hero(q.message, h)
    await q.answer()

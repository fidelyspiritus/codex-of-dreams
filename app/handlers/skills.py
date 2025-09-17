from pathlib import Path
from typing import List, Tuple

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from app.data import skills_repo as repo
from app.utils.render import skill_card

router = Router()

PER_PAGE = 10


# ------- Helpers -------
def _pairs_all() -> List[Tuple[str, str]]:
    # (name, slug)
    return [(s.name, s.slug) for s in repo.list_skills()]

def _kb_skills(pairs: List[Tuple[str, str]], page: int = 0) -> InlineKeyboardMarkup:
    start = page * PER_PAGE
    chunk = pairs[start:start + PER_PAGE]

    rows = [[InlineKeyboardButton(text=name, callback_data=f"sk:view:{slug}")]
            for name, slug in chunk]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⭠ Prev", callback_data=f"sk:list:{page - 1}"))
    if start + PER_PAGE < len(pairs):
        nav.append(InlineKeyboardButton(text="Next ⭢", callback_data=f"sk:list:{page + 1}"))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=rows)

async def _send_skill(message: types.Message, s) -> None:
    text = skill_card(s)
    img = (s.image or "").strip()
    if img:
        p = Path(img)
        if p.exists() and p.is_file():
            return await message.answer_photo(photo=FSInputFile(p), caption=text)
        if img.startswith("http://") or img.startswith("https://"):
            return await message.answer_photo(photo=img, caption=text)
    await message.answer(text)


# ------- Commands -------
@router.message(Command("skills"))
async def cmd_skills(m: types.Message):
    parts = m.text.split(maxsplit=1)

    # No query -> full list with pagination
    if len(parts) == 1:
        pairs = _pairs_all()
        if not pairs:
            return await m.answer("No skills yet.")
        return await m.answer("Select a skill:", reply_markup=_kb_skills(pairs, page=0))

    # With query -> search (simple list, no pagination for simplicity)
    q = parts[1].strip()
    hits = repo.search(q)
    if not hits:
        return await m.answer("No matches found.")
    pairs = [(s.name, s.slug) for s in hits][:30]
    await m.answer(f"Found {len(hits)} match(es). Select:", reply_markup=_kb_skills(pairs, page=0))


# ------- Callbacks -------
@router.callback_query(F.data.startswith("sk:list:"))
async def cb_list(q: types.CallbackQuery):
    try:
        page = int(q.data.split(":", 2)[2])
    except Exception:
        page = 0
    pairs = _pairs_all()
    await q.message.edit_reply_markup(reply_markup=_kb_skills(pairs, page=page))
    await q.answer()

@router.callback_query(F.data.startswith("sk:view:"))
async def cb_view(q: types.CallbackQuery):
    slug = q.data.split(":", 2)[2]
    s = repo.get_by_slug_or_name(slug)
    if not s:
        return await q.answer("Not found", show_alert=True)
    await _send_skill(q.message, s)
    await q.answer()

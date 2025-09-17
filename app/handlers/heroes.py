from pathlib import Path
from typing import List, Tuple

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from app.data import heroes_repo as repo
from app.utils.render import hero_header, hero_card, clamp_for_caption

router = Router()

PER_PAGE = 10


# ---------- Helpers ----------

def _pairs_all() -> List[Tuple[str, str]]:
    """Return (name, slug) for all heroes sorted by name."""
    return [(h.name, h.slug) for h in repo.list_heroes()]

def _kb_heroes(pairs: List[Tuple[str, str]], page: int = 0) -> InlineKeyboardMarkup:
    """Inline keyboard with pagination for heroes."""
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
    """
    Sends hero with picture if available:
    - caption: compact header (fits into Telegram caption limits)
    - full card: separate text message (Talents, Skills, Awakening lines)
    If no image found, sends the full card as a single text message.
    """
    header = clamp_for_caption(hero_header(h))   # safe short caption
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

    # Fallback: no image → send full card only
    await message.answer(full)


# ---------- Commands ----------

@router.message(Command("heroes"))
async def cmd_heroes(m: types.Message):
    """
    /heroes                -> list with pagination
    /heroes <query text>   -> search by name/specialty/season/talents/skills
    """
    parts = m.text.split(maxsplit=1)

    # No query → full list
    if len(parts) == 1:
        pairs = _pairs_all()
        if not pairs:
            return await m.answer("No heroes yet.")
        return await m.answer("Select a hero:", reply_markup=_kb_heroes(pairs, page=0))

    # With query → search
    q = parts[1].strip()
    hits = repo.search(q)
    if not hits:
        return await m.answer("No matches found.")
    pairs = [(h.name, h.slug) for h in hits][:30]
    await m.answer(f"Found {len(hits)} match(es). Select:", reply_markup=_kb_heroes(pairs, page=0))


# ---------- Callbacks ----------

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

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.data import events_repo as repo
from app.utils.render import event_card, rules_block

router = Router()

PER_PAGE = 10


# ------- Keyboards -------
def _kb_events(names: list[str], page: int = 0) -> InlineKeyboardMarkup:
    start = page * PER_PAGE
    chunk = names[start:start + PER_PAGE]

    rows = [[InlineKeyboardButton(text=n, callback_data=f"ev:view:{n}")] for n in chunk]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⭠ Prev", callback_data=f"ev:list:{page - 1}"))
    if start + PER_PAGE < len(names):
        nav.append(InlineKeyboardButton(text="Next ⭢", callback_data=f"ev:list:{page + 1}"))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def _kb_event_details(ev_id: str, has_rules: bool) -> InlineKeyboardMarkup | None:
    if not has_rules:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📜 Rules", callback_data=f"ev:rules:{ev_id}")]
        ]
    )


# ------- Commands -------
@router.message(Command("events"))
async def cmd_events(m: types.Message):
    parts = m.text.split(maxsplit=1)

    # No query -> full list with pagination
    if len(parts) == 1:
        names = [e.name for e in repo.list_events()]
        if not names:
            return await m.answer("No events yet.")
        return await m.answer("Select an event:", reply_markup=_kb_events(names, page=0))

    # With query -> search (simple list, no pagination for simplicity)
    q = parts[1].strip()
    hits = repo.search(q)
    if not hits:
        return await m.answer("No matches found.")
    names = [e.name for e in hits][:30]
    await m.answer(f"Found {len(hits)} match(es). Select:", reply_markup=_kb_events(names, page=0))


# ------- Callbacks -------
@router.callback_query(F.data.startswith("ev:list:"))
async def cb_list(q: types.CallbackQuery):
    try:
        page = int(q.data.split(":", 2)[2])
    except Exception:
        page = 0
    names = [e.name for e in repo.list_events()]
    await q.message.edit_reply_markup(reply_markup=_kb_events(names, page=page))
    await q.answer()

@router.callback_query(F.data.startswith("ev:view:"))
async def cb_view(q: types.CallbackQuery):
    name = q.data.split(":", 2)[2]
    ev = repo.get_by_name(name)
    if not ev:
        return await q.answer("Not found", show_alert=True)
    await q.message.answer(event_card(ev), reply_markup=_kb_event_details(ev.id, ev.has_rules))
    await q.answer()

@router.callback_query(F.data.startswith("ev:rules:"))
async def cb_rules(q: types.CallbackQuery):
    ev_id = q.data.split(":", 2)[2]
    ev = repo.get_by_id(ev_id)
    if not ev:
        return await q.answer("Not found", show_alert=True)
    await q.message.answer(rules_block(ev.name, ev.rules_text or "—"))
    await q.answer()

from aiogram import Router, types, F
from aiogram.filters import Command
from app.data import events_repo as repo
from app.utils.render import event_card, rules_block
from app.keyboards.events import events_list, details_kb
from app.utils.callbacks import EventCb

router = Router()

@router.message(Command("events"))
async def cmd_events(m: types.Message):
    names = [e.name for e in repo.list_events()]
    if not names:
        return await m.answer("No events yet.")
    await m.answer("Select an event:", reply_markup=events_list(names))

@router.message(Command("event"))
async def cmd_event(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) == 1:
        return await m.answer("Usage: /event <name>")
    ev = repo.get_by_name(parts[1])
    if not ev:
        return await m.answer("Event not found.")
    await m.answer(event_card(ev), reply_markup=details_kb(ev.id, ev.has_rules))

@router.message(Command("search_em"))
async def cmd_search(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) == 1:
        return await m.answer("Usage: /search_em <word>")
    hits = repo.search(parts[1])
    if not hits:
        return await m.answer("No events found.")
    await m.answer("Found:", reply_markup=events_list([e.name for e in hits]))

@router.callback_query(EventCb.filter(F.action == "view"))
async def cb_view(q: types.CallbackQuery, callback_data: EventCb):
    ev = repo.get_by_name(callback_data.id)
    if not ev:
        return await q.answer("Not found", show_alert=True)
    await q.message.answer(event_card(ev), reply_markup=details_kb(ev.id, ev.has_rules))
    await q.answer()

@router.callback_query(EventCb.filter(F.action == "page"))
async def cb_page(q: types.CallbackQuery, callback_data: EventCb):
    names = [e.name for e in repo.list_events()]
    await q.message.edit_reply_markup(reply_markup=events_list(names, page=callback_data.page))
    await q.answer()

@router.callback_query(EventCb.filter(F.action == "rules"))
async def cb_rules(q: types.CallbackQuery, callback_data: EventCb):
    ev = repo.get_by_id(callback_data.id)
    if not ev:
        return await q.answer("Not found", show_alert=True)
    await q.message.answer(rules_block(ev.name, ev.rules_text or "—"))
    await q.answer()

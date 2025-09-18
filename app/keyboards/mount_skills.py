from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ms:menu
# ms:slots:<type>
# ms:list:<type>:<slot>
# ms:item:<type>:<slot>:<index>
# ms:nav:<type>:<slot>:<index>:prev|next

def type_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Spears",   callback_data="ms:slots:spears")],
        [InlineKeyboardButton(text="Infantry", callback_data="ms:slots:infantry")],
        [InlineKeyboardButton(text="Archers",  callback_data="ms:slots:archers")],
    ])

def slots_kb(t: str) -> InlineKeyboardMarkup:
    # экран выбора слота
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Slot 1", callback_data=f"ms:list:{t}:1"),
            InlineKeyboardButton(text="Slot 2", callback_data=f"ms:list:{t}:2"),
        ],
        [InlineKeyboardButton(text="↩ Types", callback_data="ms:menu")],
    ])

def list_kb(t: str, s: int, names: list[str]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"{i+1}. {name}", callback_data=f"ms:item:{t}:{s}:{i}")]
            for i, name in enumerate(names)]
    # футер списка: другой слот + types
    other = 2 if s == 1 else 1
    rows.append([
        InlineKeyboardButton(text=f"Slot {other}", callback_data=f"ms:list:{t}:{other}"),
        InlineKeyboardButton(text="Types",        callback_data="ms:menu"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def empty_list_kb(t: str, s: int) -> InlineKeyboardMarkup:
    """Клавиатура для пустого слота: только 'Slot (другой)' и 'Types'."""
    other = 2 if s == 1 else 1
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"Slot {other}", callback_data=f"ms:list:{t}:{other}"),
            InlineKeyboardButton(text="Types",        callback_data="ms:menu"),
        ]
    ])

def item_kb(t: str, s: int, i: int, prev_i, next_i) -> InlineKeyboardMarkup:
    nav = []
    if prev_i is not None:
        nav.append(InlineKeyboardButton(text="◀ Prev", callback_data=f"ms:nav:{t}:{s}:{i}:prev"))
    if next_i is not None:
        nav.append(InlineKeyboardButton(text="Next ▶", callback_data=f"ms:nav:{t}:{s}:{i}:next"))

    rows = [nav] if nav else []
    rows += [
        [InlineKeyboardButton(text="⬅ Back to list", callback_data=f"ms:list:{t}:{s}")],
        [InlineKeyboardButton(text="↩ Types", callback_data="ms:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

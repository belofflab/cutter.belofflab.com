import math
from database.models import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


shortcuts_cd = CallbackData("show_shortcuts", "level", "spage", "sid")


def make_shortcuts_cd(level, spage="1", sid="0"):
    return shortcuts_cd.new(level=level, spage=spage, sid=sid)


async def list_shortcuts(uid: int, current_page: str):
    markup = InlineKeyboardMarkup(row_width=3)
    ushorts = (
        await UserShortcut.join(Shortcut, UserShortcut.shortcut_id == Shortcut.id)
        .select()
        .where(UserShortcut.user_id == uid)
        .gino.all()
    )
    CURRENT_PAGE = int(current_page)
    CURRENT_LEVEL = 1
    LINK_PER_PAGE = 5
    MAX_PAGES = math.ceil(len(ushorts) / LINK_PER_PAGE)
    next_page = ushorts[
        (CURRENT_PAGE * LINK_PER_PAGE) - LINK_PER_PAGE : CURRENT_PAGE * LINK_PER_PAGE
    ]
    markup.row(InlineKeyboardButton(text="Добавить", callback_data="domain#info"))
    for ushort in next_page:
        markup.row(
            InlineKeyboardButton(
                text=ushort.target_link,
                callback_data=make_shortcuts_cd(
                    level=CURRENT_LEVEL + 1, sid=ushort.shortcut_id
                ),
            )
        )
    if len(ushorts) > 0:
        markup.row(
            InlineKeyboardButton(
                text="<<",
                callback_data=make_shortcuts_cd(
                    level=CURRENT_LEVEL,
                    spage=(CURRENT_PAGE - 1) if CURRENT_PAGE != 1 else CURRENT_PAGE,
                ),
            )
        )
        markup.insert(
            InlineKeyboardButton(
                text=f"{CURRENT_PAGE}/{MAX_PAGES}", callback_data="..."
            )
        )

        markup.insert(
            InlineKeyboardButton(
                text=">>",
                callback_data=make_shortcuts_cd(
                    level=CURRENT_LEVEL,
                spage=(
                        (CURRENT_PAGE + 1)
                        if not CURRENT_PAGE >= MAX_PAGES
                        else CURRENT_PAGE
                    ),
                ),
            )
        )
    markup.row(
        InlineKeyboardButton(
            text="Назад", callback_data=make_shortcuts_cd(level=CURRENT_LEVEL - 1)
        )
    )

    return markup


async def show_shortcut(sid: int, spage: str):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(
        InlineKeyboardButton(text="Удалить", callback_data=f"domain#remove{sid}")
    )
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_shortcuts_cd(level=CURRENT_LEVEL - 1, sid=sid, spage=spage),
        )
    )

    return markup

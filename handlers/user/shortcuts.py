import secrets
import re
from data.config import WEB_APP_DOMAIN, BASE_DIR
from aiogram import types
from database import models
from keyboards.user import inline
from aiogram.dispatcher import FSMContext
from sqlalchemy.exc import IntegrityError
from states.domain import AddDomain
from .menu import start
from database.manager import shortcuts
from loader import dp, bot
from filters.is_link import IsLink

DOMAIN_REGEX = rf"https?://{WEB_APP_DOMAIN}/s/([^/]+)"
SHORTCUT_MESSAGE = f"Ссылка: https://{WEB_APP_DOMAIN}"
SHORTCUT_MESSAGE += """/s/{shortcut.code}

Цель: {shortcut.target_link}

Всего (переходы): {shortcut.click_count}
Всего (уникальные переходы): {shortcut.unique_click_count}

Уникальные переходы:
Сутки: {count_1_day[count]}
Неделя: {count_7_days[count]}
Месяц: {count_31_days[count]}
"""


@dp.message_handler(regexp=DOMAIN_REGEX)
async def handle_link_main(message: types.Message):
    link = message.text
    await message.delete()
    match = re.match(DOMAIN_REGEX, link)
    if match:
        shortcode = match.group(1)
        shortcut = await shortcuts.get_by_code(
            shortcode=shortcode, uid=message.from_user.id
        )
        if shortcut:
            flients = await shortcuts.get_forwarding_clients(shortcut.shortcut_id)
            await message.answer_photo(
                photo=types.InputFile(BASE_DIR / "data/shortenner.png"),

                caption=SHORTCUT_MESSAGE.format(shortcut=shortcut, **flients),
                reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(
                        text="Удалить",
                        callback_data=f"domain#remove{shortcut.shortcut_id}",
                    )
                ),
            )
    else:
        await message.reply("Некорректный формат ввода.")


@dp.message_handler(IsLink())
async def handle_link_any(message: types.Message, state: FSMContext):

    link = message.text
    await message.delete()
    if WEB_APP_DOMAIN in link:
        return await message.answer_photo(
            photo=types.InputFile(BASE_DIR / "data/shortenner.png"),
            caption="Мы не нашли ссылку в базе...",
        )
    shortcut = await shortcuts.get_by_tlink(target_link=link, uid=message.from_user.id)
    if shortcut:
        flients = await shortcuts.get_forwarding_clients(shortcut.shortcut_id)
        await message.answer_photo(
            photo=types.InputFile(BASE_DIR / "data/shortenner.png"),
            caption=SHORTCUT_MESSAGE.format(shortcut=shortcut, flients=flients),
            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton(
                    text="Удалить", callback_data=f"domain#remove{shortcut.shortcut_id}"
                )
            ),
        )
    else:
        await AddDomain.target_link.set()
        new_message = await message.answer_photo(
            photo=types.InputFile(BASE_DIR / "data/shortenner.png"),
            caption=f"Вы хотите добавить в базу {link}?",
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(
                    text="Да", callback_data="add_domain#accept"
                ),
                types.InlineKeyboardButton(
                    text="Отмена", callback_data="add_domain#reject"
                ),
            ),
        )
        await state.set_data({"link": link, "last_message_id": new_message.message_id})


async def generate_unique_shortcut(target_link, max_attempts=25, code_length=8):
    for _ in range(max_attempts):
        code = secrets.token_urlsafe(code_length)[:code_length]
        try:
            shortcut = await models.Shortcut.create(code=code, target_link=target_link)
            return shortcut
        except IntegrityError:
            pass
    raise ValueError(
        f"Failed to generate a unique shortcut after {max_attempts} attempts"
    )


@dp.callback_query_handler(lambda c: c.data.startswith("domain"))
async def domain_steps(callback: types.CallbackQuery, state: FSMContext):
    do = callback.data.split("#")[-1]
    if do == "info":
        await callback.answer("Просто пришлите мне целевую ссылку!", show_alert=True)
    elif "remove" in do:
        sid = do.split("remove")[-1]
        await callback.message.edit_caption(
            caption="Вы уверены, что хотите удалить?",
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(
                    text="Да", callback_data=f"remove_domain#{sid}#yes"
                ),
                types.InlineKeyboardButton(
                    text="Нет", callback_data=f"remove_domain#{sid}#no"
                ),
            ),
        )


@dp.callback_query_handler(lambda c: c.data.startswith("remove_domain"))
async def remove_domain_confirm(callback: types.CallbackQuery):
    splitted_data = callback.data.split("#")
    sid = splitted_data[1]
    res = splitted_data[2]
    if res == "yes":
        await shortcuts.delete(int(sid))
        await list_shortcuts(callback=callback, spage=1)
    elif res == "no":
        await show_shortcut(callback=callback, sid=sid, spage=1)


@dp.callback_query_handler(
    lambda c: c.data.startswith("add_domain"), state=AddDomain.target_link
)
async def target_link_set(callback: types.CallbackQuery, state: FSMContext):
    do = callback.data.split("#")[-1]
    if do == "reject":
        await state.finish()
        return await start(callback)
    async with state.proxy() as data:
        last_message_id = data["last_message_id"]
        link = data["link"]
        new_shortcut = await generate_unique_shortcut(target_link=link)
        await models.UserShortcut.create(
            user_id=callback.from_user.id,
            shortcut_id=new_shortcut.id,
        )
        await state.finish()
        flients = await shortcuts.get_forwarding_clients(new_shortcut.id)
        await bot.edit_message_caption(
            chat_id=callback.from_user.id,
            caption=SHORTCUT_MESSAGE.format(shortcut=new_shortcut, **flients),
            message_id=last_message_id,
            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton(
                    text="Назад",
                    callback_data=inline.make_shortcuts_cd(level=1),
                ),
                types.InlineKeyboardButton(
                    text="Удалить", callback_data=f"domain#remove{new_shortcut.id}"
                ),
            ),
        )


async def list_shortcuts(callback: types.CallbackQuery, spage: str, **kwargs):
    markup = await inline.list_shortcuts(uid=callback.from_user.id, current_page=spage)
    await callback.message.edit_caption(
        caption="Выберите ссылку:",
        reply_markup=markup,
    )


async def show_shortcut(callback: types.CallbackQuery, sid: str, spage: str, **kwargs):
    markup = await inline.show_shortcut(sid=sid, spage=spage)
    shortcut = await shortcuts.get_by_id(sid=sid, uid=callback.from_user.id)
    flients = await shortcuts.get_forwarding_clients(shortcut.shortcut_id)
    await callback.message.edit_caption(
        caption=SHORTCUT_MESSAGE.format(shortcut=shortcut, **flients),
        reply_markup=markup,
    )


@dp.callback_query_handler(inline.shortcuts_cd.filter())
async def marketplace_navigate(
    callback: types.CallbackQuery, state: FSMContext, callback_data: dict
):
    level = callback_data.get("level")
    spage = callback_data.get("spage")
    sid = callback_data.get("sid")

    levels = {"0": start, "1": list_shortcuts, "2": show_shortcut}

    current_level = levels[level]

    await current_level(callback, state=state, spage=spage, sid=sid)

from aiogram import types
from database import models
from typing import Union
from data.config import BASE_DIR, SUPPORT_LINK
from keyboards.user import inline
from filters.is_admin import IsAdmin
from loader import dp


async def get_or_create_user(message: types.Message):
    s_user = await models.User.query.where(
        models.User.id == message.from_user.id
    ).gino.first()
    if s_user is None:
        s_user = await models.User.create(
            id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
    else:
        if (
            s_user.username != message.from_user.username
            or s_user.full_name != message.from_user.full_name
        ):
            await s_user.update(
                username=message.from_user.username,
                full_name=message.from_user.full_name,
            ).apply()
    return s_user


@dp.message_handler(IsAdmin(), commands="start")
async def start(message: Union[types.Message, types.CallbackQuery], **kwargs) -> None:
    user: models.User = await get_or_create_user(message=message)
    if isinstance(message, types.Message):
        await message.answer_photo(
            photo=types.InputFile(BASE_DIR / "data/shortenner.png"),
            caption=f"""
Добро пожаловать, <b>{user.full_name}!</b>

Для генерации ссылки просто пришлите её в чат!
""",
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(
                    text="Мои ссылки",
                    callback_data=inline.make_shortcuts_cd(level=1),
                ),
                types.InlineKeyboardButton(text="Поддержка", url=SUPPORT_LINK),
            ),
        )
    elif isinstance(message, types.CallbackQuery):
        await message.message.edit_media(
            media=types.InputMediaPhoto(
                media=types.InputFile(BASE_DIR / "data/shortenner.png"),
                caption=f"""
Добро пожаловать, <b>{user.full_name}!</b>

Для генерации ссылки просто пришлите её в чат!


""",
            ),
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(
                    text="Мои ссылки",
                    callback_data=inline.make_shortcuts_cd(level=1),
                ),
                types.InlineKeyboardButton(text="Поддержка", url=SUPPORT_LINK),
            ),
        )

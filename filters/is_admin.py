from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery
from data.config import ADMIN_IDS
from loader import bot

class IsAdmin(BoundFilter):
    async def check(_, callback: CallbackQuery):
        if callback.from_user.id in ADMIN_IDS:
            return True
        return False
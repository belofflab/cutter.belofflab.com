from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery
from data.config import CHANNEL_ID
from loader import bot
from keyboards.user import inline

class IsChatMember(BoundFilter):
    async def check(_, callback: CallbackQuery):
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id= callback.from_user.id)
        if not member.status == "left":
                return True
        await bot.send_message(chat_id=callback.from_user.id, text="""
Чтобы использоваться бот, для начала подпишитесь на наш канал!
      
""")
        return False 
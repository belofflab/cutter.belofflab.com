import re
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

class IsLink(BoundFilter):
    async def check(self, message: Message) -> bool:
        link_pattern = re.compile(r"https?://\S+")
        return bool(link_pattern.match(message.text))
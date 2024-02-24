import re
from data.config import BASE_DIR
from aiogram import types
from database import models
from keyboards.user import inline
from aiogram.dispatcher import FSMContext
from pornhub_api.backends.aiohttp import AioHttpBackend
from pornhub_api import PornhubApi
from pornhub_api.exceptions.response import NoVideoError
from loader import dp


@dp.inline_handler()
async def inline_search(query: types.InlineQuery):
    FIRST_PAGE = 1
    query_offset = int(query.offset) if query.offset else FIRST_PAGE
    async with AioHttpBackend() as backend:
        api = PornhubApi(backend=backend)
        try:
            videos = await api.search.search_videos(
                query.query,
                ordering="mostviewed",
                period="weekly",
                page=query_offset
            )
        except NoVideoError:
            videos = await api.search.search_videos(
                query.query,
                ordering="mostviewed",
                period="weekly",
                page=FIRST_PAGE
            )
        results = [
            types.InlineQueryResultArticle(
                id=video.video_id,
                title=video.title,
                input_message_content=types.InputTextMessageContent(
                    message_text=(
                        f"<b>{video.title}</b>\n\n"
                        f"{'<b>Звезды: </b>' + ', '.join([pornstar.pornstar_name for pornstar in video.pornstars]) if video.pornstars else ''}\n"
                        f"<b>Продолжительность:</b> {video.duration}\n\n"
                        f"{' '.join(['#' + tag.tag_name.replace(' ', '_') for tag in video.tags])}\n\n"
                        f"<a href='{video.url}'>Смотреть</a> <a href='https://t.me/linkShorterBBot?start=dl{video.video_id}'>Скачать</a>"
                    ),
                    disable_web_page_preview=True,
                ),
                description=f"Продолжительность: {video.duration}\nРейтинг: {video.rating}\nПросмотры: {video.views}",
                thumb_url=str(video.thumb),
            )
            for video in videos
        ]
        await query.answer(
            results,
            switch_pm_text="• Результаты •",
            switch_pm_parameter="start",
            next_offset=query_offset+1
        )
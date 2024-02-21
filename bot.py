import aiohttp_cors
from sqlalchemy import and_
from aiohttp.web_app import Application
from aiohttp_cors import CorsViewMixin
from aiogram.dispatcher.webhook import get_new_configured_app
from database.models import db
from user_agents import parse
from data.config import (
    DATABASE_URL,
    WEB_APP_HOST,
    WEB_APP_PORT,
    WEB_APP_WEBHOOK,
)
from aiohttp import web
from database.models import Shortcut, ForwardingClient, ShortcutClient
from loader import dp


class ShortCutView(web.View, CorsViewMixin):
    async def get(self):
        shortcut_id = self.request.match_info["shortcut_id"]
        ip_address = self.request.headers.get("X-Forwarded-For") or self.request.remote
        user_agent_string = self.request.headers.get("User-Agent")
        user_agent = parse(user_agent_string)

        if not user_agent.is_bot and not "other" in str(user_agent):
            shortcut = await Shortcut.query.where(
                Shortcut.code == shortcut_id
            ).gino.first()

            if shortcut:
                existing_client = await ForwardingClient.query.where(
                    ForwardingClient.ip_address == ip_address
                ).gino.first()
                if existing_client is not None:
                    existing_forward = await ShortcutClient.query.where(
                        and_(
                            ShortcutClient.client_id == existing_client.id,
                            ShortcutClient.shortcut_id == shortcut.id,
                        )
                    ).gino.first()
                else:
                    existing_forward = None

                if not existing_forward:
                    if not existing_client:
                        new_client = await ForwardingClient.create(
                            ip_address=ip_address
                        )
                        client_id = new_client.id
                    else:
                        client_id = existing_client.id
                    await ShortcutClient.create(
                        shortcut_id=shortcut.id, client_id=client_id
                    )
                    await shortcut.update(
                        click_count=Shortcut.click_count + 1,
                        unique_click_count=Shortcut.unique_click_count + 1,
                    ).apply()
                else:
                    await shortcut.update(click_count=Shortcut.click_count + 1).apply()
                return web.HTTPFound(location=shortcut.target_link)
            else:
                return web.HTTPNotFound(text="Shortcut not found")
        else:
            return web.HTTPForbidden(text="Bot requests are not allowed")


async def on_startup(app: Application):
    await db.set_bind(DATABASE_URL)

    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    cors.add(app.router.add_view("/s/{shortcut_id}", ShortCutView))


if __name__ == "__main__":
    import handlers

    app = get_new_configured_app(dp, path=WEB_APP_WEBHOOK)
    app.on_startup.append(on_startup)
    web.run_app(app, host=WEB_APP_HOST, port=WEB_APP_PORT)

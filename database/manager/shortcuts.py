from datetime import datetime, timedelta
from sqlalchemy import and_
from database.models import Shortcut, UserShortcut, ShortcutClient


async def delete(shortcut_id):
    shortcut = await Shortcut.query.where(Shortcut.id == shortcut_id).gino.first()
    if shortcut:
        user_shortcut = await UserShortcut.query.where(
            UserShortcut.shortcut_id == shortcut_id
        ).gino.first()
        if user_shortcut:
            await user_shortcut.delete()

        await shortcut.delete()
    else:
        print(f"Shortcut with id {shortcut_id} not found.")


async def get_by_id(sid, uid):
    shortcut = (
        await UserShortcut.join(Shortcut, UserShortcut.shortcut_id == Shortcut.id)
        .select()
        .where(
            and_(
                UserShortcut.user_id == uid,
                Shortcut.id == int(sid),
            )
        )
        .gino.first()
    )
    return shortcut


async def get_by_code(shortcode, uid):
    shortcut = (
        await UserShortcut.join(Shortcut, UserShortcut.shortcut_id == Shortcut.id)
        .select()
        .where(
            and_(
                UserShortcut.user_id == uid,
                Shortcut.code == shortcode,
            )
        )
        .gino.first()
    )
    return shortcut


async def get_by_tlink(target_link, uid):
    shortcut = (
        await UserShortcut.join(Shortcut, UserShortcut.shortcut_id == Shortcut.id)
        .select()
        .where(
            and_(
                UserShortcut.user_id == uid,
                Shortcut.target_link == target_link,
            )
        )
        .gino.first()
    )
    return shortcut


async def get_forwarding_clients(sid: str) -> dict:
    UPPER_LIMIT = 31
    UPPER_LIMIT_NAME = "Месяц"
    UPPER_LIMIT_KEY = "count_31_days"
    steps = {
        "count_1_day": {"delta": 1, "name": "Сутки", "count": 0, "data": []},
        "count_7_days": {"delta": 7, "name": "Неделя", "count": 0, "data": []},
    }
    end_date = datetime.now()
    flients = await ShortcutClient.query.where(
        and_(
            ShortcutClient.shortcut_id == int(sid),
            ShortcutClient.created_at >= end_date - timedelta(days=UPPER_LIMIT),
            ShortcutClient.created_at <= end_date,
        )
    ).gino.all()
    for key, value in steps.items():
        flients = [
            el
            for el in flients
            if el.created_at >= end_date - timedelta(days=value["delta"])
            and el.created_at <= end_date
        ]
        steps[key]["data"] = flients
        steps[key]["count"] = len(flients)
    steps.update(
        {
            UPPER_LIMIT_KEY: {
                "delta": UPPER_LIMIT,
                "name": UPPER_LIMIT_NAME,
                "count": len(flients),
                "data": flients,
            }
        }
    )
    return steps

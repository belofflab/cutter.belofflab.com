import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__name__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE)

SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/support")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = [int(aid) for aid in os.getenv("ADMIN_IDS").split(" ")]

WEB_APP_DOMAIN = os.getenv("WEB_APP_DOMAIN")
WEB_APP_HOST = os.getenv("WEB_APP_HOST")
WEB_APP_PORT = int(os.getenv("WEB_APP_PORT", 6712))
WEB_APP_WEBHOOK = os.getenv("WEB_APP_WEBHOOK")

WEB_APP_URL = WEB_APP_DOMAIN + WEB_APP_WEBHOOK

CHANNEL_ID = int(os.getenv("CHANNEL_ID", -100))

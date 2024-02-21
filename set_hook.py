import requests
from data.config import WEB_APP_URL, BOT_TOKEN


res = requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEB_APP_URL}"
)

print(res.json())

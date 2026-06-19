import os

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mirjalolbekqosimjonov-coder.github.io/mebel-webapp")

_ids = os.getenv("ADMIN_IDS", "520713609")
ADMIN_IDS = [int(x) for x in _ids.split(",") if x.strip()]

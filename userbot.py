# userbot.py
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

if not API_ID or not API_HASH or not STRING_SESSION:
    raise RuntimeError("API_ID / API_HASH / STRING_SESSION missing")

bot = TelegramClient(
    StringSession(STRING_SESSION),
    int(API_ID),
    API_HASH
)

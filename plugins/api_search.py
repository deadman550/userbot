# plugins/api_search.py
# API SEARCH (Numverify) – SAFE + DISABLABLE VERSION

import asyncio
import requests
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_control import is_disabled

PLUGIN_NAME = "api_search"
print("✔ api_search.py loaded (API SEARCH MODE)")

# =====================
# CONFIG
# =====================
# ⚠️ Better to set this as ENV VAR
# export NUMVERIFY_API_KEY=your_key_here
import os
API_KEY = os.getenv("NUMVERIFY_API_KEY")

API_URL = "http://apilayer.net/api/validate"
TIMEOUT = 15  # seconds

# =====================
# HELP
# =====================
register_help(
    "search",
    ".search <number>\n\n"
    "• Phone number lookup (Numverify)\n"
    "• Plugin on/off supported\n"
    "• API based search"
)

# =====================
# SEARCH COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.search\s+(.+)"))
async def api_search(e):
    # 🔴 PLUGIN DISABLED CHECK
    if is_disabled(PLUGIN_NAME):
        return

    try:
        query = e.pattern_match.group(1).strip()
        if not query:
            return await e.reply("❌ Provide a number to search")

        if not API_KEY:
            return await e.reply("❌ API key not configured")

        msg = await e.reply("🔍 Searching number info...")

        params = {
            "access_key": API_KEY,
            "number": query,
            "format": 1
        }

        r = requests.get(API_URL, params=params, timeout=TIMEOUT)

        if r.status_code != 200:
            await msg.edit("❌ API error (non-200 response)")
            return

        data = r.json()

        # ❌ invalid number / API failure
        if not data.get("valid"):
            await msg.edit("❌ Invalid number or no data found")
            return

        number = data.get("international_format", "N/A")
        country = data.get("country_name", "N/A")
        location = data.get("location", "N/A")
        carrier = data.get("carrier", "N/A")
        line_type = data.get("line_type", "N/A")

        text = (
            "📄 **NUMBER LOOKUP RESULT**\n\n"
            f"📞 Number: `{number}`\n"
            f"🌍 Country: `{country}`\n"
            f"📍 Location: `{location}`\n"
            f"📡 Carrier: `{carrier}`\n"
            f"📶 Line Type: `{line_type}`\n\n"
            f"🔎 Query: `{query}`"
        )

        await msg.edit(text)

    except requests.exceptions.Timeout:
        await e.reply("⚠️ API timeout, try again later")
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        await e.reply("❌ Unexpected error occurred")

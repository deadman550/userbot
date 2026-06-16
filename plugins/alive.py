# plugins/alive.py

import time
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.health import get_uptime, mongo_status
from utils.logger import log_error

PLUGIN_NAME = "alive.py"

print(f"✔ {PLUGIN_NAME} loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "alive",
    ".alive\n"
    ".ping\n\n"
    "• Check userbot status\n"
    "• Ping & uptime info\n"
    "• Owner only"
)

# =====================
# ALIVE COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.alive$"))
async def alive_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        text = (
            "🤖 **Userbot Alive**\n\n"
            f"⏱ **Uptime:** {get_uptime()}\n"
            f"🗄 **MongoDB:** {mongo_status()}\n"
            "🚀 **Status:** Running"
        )

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)


# =====================
# PING COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.ping$"))
async def ping_cmd(e):
    if not is_owner(e):
        return

    try:
        start = time.time()
        await e.delete()

        msg = await bot.send_message(e.chat_id, "🏓 Pinging...")
        end = time.time()

        ping_ms = int((end - start) * 1000)

        await msg.edit(f"🏓 **Pong!** `{ping_ms} ms`")
        await asyncio.sleep(4)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

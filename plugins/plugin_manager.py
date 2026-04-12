# plugins/plugin_manager.py

import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_control import enable, disable
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded
from utils.logger import log_error

PLUGIN_NAME = "plugin_manager"
mark_plugin_loaded(PLUGIN_NAME)
print("✔ plugin_manager.py loaded")

# =====================
# CONFIG
# =====================
AUTO_DEL = 8   # seconds

# =====================
# TEMP MESSAGE
# =====================
async def temp_msg(chat_id, text, reply_to=None, delay=AUTO_DEL):
    m = await bot.send_message(chat_id, text, reply_to=reply_to)
    await asyncio.sleep(delay)
    await m.delete()

# =====================
# HELP
# =====================
register_help(
    "plugin",
    ".plugin on <name>\n"
    ".plugin off <name>\n"
    ".pluginstatus\n\n"
    "• Enable / Disable plugins\n"
    "• Owner only\n"
    "• Auto delete output"
)

# =====================
# LIST PLUGINS
# =====================
@bot.on(events.NewMessage(pattern=r"\.pluginstatus$"))
async def list_plugins(e):
    if not is_owner(e):
        return

    await e.delete()  # 🔥 command delete

    try:
        from utils.plugin_control import _load
        data = _load()

        if not data:
            await temp_msg(e.chat_id, "ℹ️ No plugin state data found")
            return

        text = "🧩 **PLUGIN STATUS**\n\n"
        for name, state in data.items():
            emoji = "✅" if state else "⛔"
            text += f"{emoji} `{name}`\n"

        await temp_msg(e.chat_id, text)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# ENABLE / DISABLE
# =====================
@bot.on(events.NewMessage(pattern=r"\.plugin (on|off) (\w+)$"))
async def toggle_plugin(e):
    if not is_owner(e):
        return

    await e.delete()  # 🔥 command delete

    try:
        action, name = e.pattern_match.groups()

        if action == "on":
            enable(name)
            await temp_msg(e.chat_id, f"✅ Plugin `{name}` enabled")
        else:
            disable(name)
            await temp_msg(e.chat_id, f"⛔ Plugin `{name}` disabled")

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

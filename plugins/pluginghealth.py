import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import PLUGIN_STATUS

print("✔ pluginhealth.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "pluginhealth",
    ".plugins\n\n"
    "Shows health status of all plugins\n"
    "• ❌ = plugin has error\n"
    "• ✅ = plugin working fine\n"
    "• Shows last error if failed"
)

# =====================
# PLUGINS HEALTH COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.plugins$"))
async def plugin_health_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except Exception:
            pass

        if not PLUGIN_STATUS:
            msg = await bot.send_message(
                e.chat_id,
                "No plugin health data available"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        text = "🩺 PLUGIN HEALTH STATUS\n\n"

        for plugin, info in PLUGIN_STATUS.items():
            if info.get("status") == "error":
                text += (
                    f"❌ {plugin}\n"
                    f"Error: {info.get('error')}\n\n"
                )
            else:
                text += f"✅ {plugin}\n"

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(25)
        await msg.delete()

    except Exception:
        await log_error(bot, "pluginhealth.py")
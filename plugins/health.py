import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_status import get_broken_plugins, mark_plugin_loaded
from utils.health import get_uptime, mongo_status
from utils.auto_delete import auto_delete

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("health.py")
print("✔ health.py loaded")

# =====================
# HEALTH COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.health$"))
async def health_handler(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    broken = get_broken_plugins()

    if not broken:
        text = (
            "🩺 **Userbot Health**\n\n"
            f"⏱ **Uptime:** {get_uptime()}\n"
            f"🗄 **MongoDB:** {mongo_status()}\n\n"
            "✅ **All plugins working fine**"
        )
        msg = await bot.send_message(e.chat_id, text)
        return await auto_delete(msg, 8)

    text = (
        "🩺 **Userbot Health**\n\n"
        f"⏱ **Uptime:** {get_uptime()}\n"
        f"🗄 **MongoDB:** {mongo_status()}\n\n"
        "❌ **Broken Plugins:**\n"
    )

    for name, info in broken.items():
        text += f"\n• **{name}**\n`{info['error'][:400]}`"

    msg = await bot.send_message(e.chat_id, text)
    await auto_delete(msg, 15)

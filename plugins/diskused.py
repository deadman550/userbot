# plugins/diskused.py

import os
import asyncio

from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "diskused.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ diskused.py loaded")

# =====================
# HELP
# =====================
register_help(
    "diskused",
    ".diskused\n\n"
    "• Shows disk usage\n"
    "• Folder-wise breakdown\n"
    "• Read-only (safe)"
)

# =====================
# CONFIG
# =====================
CHECK_FOLDERS = [
    "saved_media",
    "assets",
    "utils",
    "data",
    "plugins",
    "downloads"
]

# =====================
# UTILS
# =====================
def folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

def fmt(size):
    mb = size / (1024 * 1024)
    gb = mb / 1024
    return f"{mb:.2f} MB ({gb:.2f} GB)"

# =====================
# COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.diskused$"))
async def disk_used(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        total = 0
        text = "💽 **DISK USAGE REPORT**\n\n"

        for folder in CHECK_FOLDERS:
            if os.path.exists(folder):
                size = folder_size(folder)
                total += size
                text += f"📁 `{folder}` → {fmt(size)}\n"
            else:
                text += f"📁 `{folder}` → 0 MB\n"

        text += "\n━━━━━━━━━━━━━━\n"
        text += f"🧮 **TOTAL USED:** {fmt(total)}"

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

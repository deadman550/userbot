# Shadow Clone Jutsu Plugin
# Converted for Telethon Userbot (Ultroid-style animation)

import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "shadowclone.py"
print("✔ shadowclone.py loaded")

# Naruto sticker file_ids
STICKERS = [
    "CAADBQADTQQAAjIGoVZ7OvJtD0u3gwI",
    "CAADBQADgQIAAv0HqVYf8g-XlFYo2gI",
    "CAADBQADiQUAAj_woFaF8Va36nUjUgI",
    "CAADBQADBgIAAi7IoVasfvifJ20FwQI",
    "CAADBQADKQIAAuqfoVY1KwWWaeAb8QI",
]

FINAL_IMAGE = "https://telegra.ph/file/2d5c219f6147e5fc59a89.jpg"


@bot.on(events.NewMessage(pattern=r"\.shadowclone$"))
async def shadowclone(e):
    try:
        # delete command message
        await e.delete()

        # sticker animation
        for sticker in STICKERS:
            msg = await bot.send_file(e.chat_id, sticker)
            await asyncio.sleep(1.5)
            await msg.delete()

        await asyncio.sleep(1)

        # final text
        text = await bot.send_message(e.chat_id, "Shadow Clone Jutsu!!")
        await asyncio.sleep(1)
        await text.delete()

        # final image
        await bot.send_file(e.chat_id, FINAL_IMAGE)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "shadowclone",
    ".shadowclone\n\n"
    "• Naruto style shadow clone animation\n"
    "• Stickers appear & disappear\n"
    "• Final image reveal"
)
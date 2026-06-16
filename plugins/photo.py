# Profile Photo Fetcher Plugin
# Converted for Telethon Userbot
# Inspired by Ultroid / DC

import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "poto.py"
print("✔ poto.py loaded (Profile Photos)")


@bot.on(events.NewMessage(pattern=r"\.poto(?:\s+(\d+))?$"))
async def poto_handler(e):
    try:
        index = e.pattern_match.group(1)

        # determine target
        if e.is_reply:
            reply = await e.get_reply_message()
            user = await reply.get_sender()
        else:
            user = await e.get_sender()

        # get all profile photos
        photos = await bot.get_profile_photos(user.id)

        if not photos:
            return await e.edit("❌ This user has no profile photos.")

        # if no index → send all
        if not index:
            await e.delete()
            await bot.send_file(e.chat_id, photos)
            return

        index = int(index)
        if index <= 0:
            return await e.edit("❌ Invalid photo number.")

        if index > len(photos):
            return await e.edit("❌ No photo found at this index.")

        # send specific photo
        photo = photos[index - 1]
        await e.delete()
        await bot.send_file(e.chat_id, photo)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "poto",
    ".poto (reply optional)\n"
    ".poto <number>\n\n"
    "• Fetch user profile photos\n"
    "• Reply to get target user's photos\n"
    "• Provide number to get specific photo"
)
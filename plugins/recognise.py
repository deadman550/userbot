# plugins/recognise.py

import asyncio
from telethon import events
from telethon.errors import YouBlockedUserError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

PLUGIN_NAME = "recognise.py"
REKOG_BOT = "@Rekognition_Bot"
REKOG_BOT_ID = 461083923

print("✔ recognise.py loaded")

# =====================
# HELP
# =====================
register_help(
    "recognise",
    ".recognise\n\n"
    "Reply to an image or media.\n"
    "Uses AWS Rekognition to detect:\n"
    "• Labels\n"
    "• Text\n"
    "• Faces\n"
    "• Moderation tags"
)

# =====================
# RECOGNISE COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.recognise$"))
async def recognise(event):
    if not is_owner(event):
        return

    if not event.is_reply:
        msg = await event.reply("❌ Reply to an image/media")
        await asyncio.sleep(3)
        return await msg.delete()

    reply = await event.get_reply_message()

    # ❌ bot message
    if reply.sender and reply.sender.bot:
        msg = await event.reply("❌ Reply to a real user's media")
        await asyncio.sleep(3)
        return await msg.delete()

    # ❌ no media
    if not reply.media:
        msg = await event.reply("❌ Reply to an image or media file")
        await asyncio.sleep(3)
        return await msg.delete()

    # only image/video/doc
    if not isinstance(
        reply.media,
        (MessageMediaPhoto, MessageMediaDocument)
    ):
        msg = await event.reply("❌ Unsupported media type")
        await asyncio.sleep(3)
        return await msg.delete()

    await event.delete()
    status = await event.respond("🔍 Recognising image…")
    
    try:
        async with bot.conversation(REKOG_BOT, timeout=90) as conv:
            await bot.forward_messages(REKOG_BOT, reply)

            response = await conv.wait_event(
                events.NewMessage(incoming=True, from_users=REKOG_BOT_ID)
            )

            # sometimes bot says "See next message."
            if response.text and response.text.startswith("See next message"):
                response = await conv.wait_event(
                    events.NewMessage(incoming=True, from_users=REKOG_BOT_ID)
                )

            await status.edit(response.text or "❌ No result found")

    except YouBlockedUserError:
        await status.edit("❌ Unblock @Rekognition_Bot and try again")

    except asyncio.TimeoutError:
        await status.edit("❌ Recognition timed out")

    except Exception as e:
        await log_error(bot, PLUGIN_NAME, e)
        await status.edit("❌ Error while recognising")

import os
import uuid
import asyncio
from datetime import datetime
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ ss.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "media",
    ".ss (reply)\n\n"
    "• Saves self-destruct / view-once media\n"
    "• Media forwarded to Saved Messages\n"
    "• Local file auto-deletes"
)

# =====================
# CONFIG
# =====================
TARGET_CHAT = "me"
SAVE_DIR = "saved_media"
os.makedirs(SAVE_DIR, exist_ok=True)

# =====================
# SS HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.ss$"))
async def ss_handler(e):
    if not is_owner(e):
        return

    try:
        # delete command
        try:
            await e.delete()
        except Exception:
            pass

        if not e.is_reply:
            return

        reply = await e.get_reply_message()
        if not reply or not reply.media:
            return

        # 🔥 ONLY self-destruct / view-once media
        ttl = getattr(reply.media, "ttl_seconds", None)
        if not ttl:
            return

        # 🔤 filename
        if reply.file and reply.file.name:
            filename = reply.file.name
        else:
            ext = (
                ".jpg" if reply.photo else
                ".mp4" if reply.video or reply.gif else
                ".mp3" if reply.audio else
                ".bin"
            )
            filename = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                f"{uuid.uuid4().hex[:6]}{ext}"
            )

        path = os.path.join(SAVE_DIR, filename)

        # ⬇️ download media (temporary)
        await bot.download_media(reply, file=path)

        # 📤 send to Saved Messages
        await bot.send_file(
            TARGET_CHAT,
            path,
            caption=(
                "🔥 Self-destruct media saved\n\n"
                f"Chat ID: {reply.chat_id}\n"
                f"Message ID: {reply.id}\n"
                f"Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
            )
        )

        # 🧹 delete local file
        try:
            os.remove(path)
        except Exception:
            pass

        # ✅ confirmation
        msg = await bot.send_message(
            e.chat_id,
            "✅ Saved to Saved Messages"
        )
        await asyncio.sleep(5)
        await msg.delete()

    except Exception:
        await log_error(bot, "ss.py")
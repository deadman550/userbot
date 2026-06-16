import os
import random
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "neko",
    "<b>😺 Neko Media Engine</b>\n\n"
    "<b>Commands:</b>\n"
    "• <code>.neko</code> | <code>.nekokiss</code>\n"
    "• <code>.nekohug</code> | <code>.nekoslap</code>\n"
    "• <code>.nekofuck</code> | <code>.nekolick</code>\n\n"
    "<b>Features:</b>\n"
    "• Random media from assets folder.\n"
    "• Auto-delete media after 30s.\n"
    "• Error logs auto-delete after 6s."
)

# =====================
# CONFIG
# =====================
NEKO_FOLDERS = {
    "neko": "assets/neko",
    "nekokiss": "assets/nekokiss",
    "nekolick": "assets/nekolick", # 👈 Added
    "nekohug": "assets/nekohug",
    "nekofuck": "assets/nekofuck",
    "nekoslap": "assets/nekoslap",
}

SUPPORTED_EXT = (
    ".jpg", ".jpeg", ".png",
    ".gif", ".webp", ".mp4"
)

# =====================
# HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.(neko|nekokiss|nekolick|nekohug|nekoslap|nekofuck)$"))
async def neko_handler(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except Exception:
            pass

        cmd = e.pattern_match.group(1)
        folder = NEKO_FOLDERS.get(cmd)

        if not folder or not os.path.isdir(folder):
            msg = await bot.send_message(
                e.chat_id,
                f"❌ <b>Folder missing:</b> <code>{cmd}</code>",
                parse_mode="html"
            )
            await asyncio.sleep(6) # 6 second delay for errors
            await msg.delete()
            return

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(SUPPORTED_EXT)
        ]

        if not files:
            msg = await bot.send_message(
                e.chat_id,
                f"❌ <b>No media found in:</b> <code>{cmd}</code>",
                parse_mode="html"
            )
            await asyncio.sleep(6)
            await msg.delete()
            return

        file_path = os.path.join(folder, random.choice(files))

        sent = await bot.send_file(
            e.chat_id,
            file_path,
            caption=f"😺 <b>{cmd.upper()}~</b>",
            parse_mode="html"
        )

        # auto delete after 30 sec
        await asyncio.sleep(30)
        await sent.delete()

    except Exception:
        await log_error(bot, "neko.py")

print("✔ neko.py loaded with .nekolick")

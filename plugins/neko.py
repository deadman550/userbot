import os
import random
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

print("✔ neko.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "neko",
    ".neko\n"
    ".nekokiss\n"
    ".nekohug\n"
    ".nekoslap\n"
    ".nekofuck\n\n"
    "• Sends random neko media\n"
    "• Files loaded from assets folder\n"
    "• Auto delete after 30 seconds\n"
    "• Owner only"
)

# =====================
# CONFIG
# =====================
NEKO_FOLDERS = {
    "neko": "assets/neko",
    "nekokiss": "assets/nekokiss",
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
@bot.on(events.NewMessage(pattern=r"\.(neko|nekokiss|nekohug|nekoslap|nekofuck)$"))
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
                f"❌ Folder missing for {cmd}"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(SUPPORTED_EXT)
        ]

        if not files:
            msg = await bot.send_message(
                e.chat_id,
                f"❌ No media found for {cmd}"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        file_path = os.path.join(folder, random.choice(files))

        sent = await bot.send_file(
            e.chat_id,
            file_path,
            caption=f"😺 {cmd}~"
        )

        # auto delete after 30 sec
        await asyncio.sleep(30)
        await sent.delete()

    except Exception:
        await log_error(bot, "neko.py")
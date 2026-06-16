import os
import sys
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ restart.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "basic",
    ".restart\n\n"
    "Restarts the userbot safely\n"
    "• Sends confirmation after restart"
)

# =====================
# RESTART COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.restart$"))
async def restart_cmd(e):
    if not is_owner(e):
        return

    try:
        # 1️⃣ delete command
        try:
            await e.delete()
        except Exception:
            pass

        # 2️⃣ restarting message
        await bot.send_message(
            e.chat_id,
            "♻️ Restarting userbot..."
        )

        # 3️⃣ save chat id for after-restart message
        os.environ["RESTART_CHAT"] = str(e.chat_id)

        # 4️⃣ small delay to ensure message is sent
        await asyncio.sleep(1)

        # 5️⃣ restart process
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception:
        await log_error(bot, "restart.py")
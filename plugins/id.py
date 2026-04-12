# plugins/id.py
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ id.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "info",
    ".id\n"
    "Get your ID, chat ID, replied user ID, or channel ID."
)

# =====================
# ID COMMAND (FIXED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.id(?:\s+.*)?$"))
async def get_id(e):
    if not is_owner(e):
        return

    try:
        # delete command safely
        try:
            await e.delete()
        except:
            pass

        text = "🆔 ID INFO\n\n"

        # 👤 YOUR ID
        text += f"🙋 Your ID: {e.sender_id}\n"

        # 💬 CHAT INFO
        text += f"💬 Chat ID: {e.chat_id}\n"

        # 🔐 PRIVATE CHAT
        if e.is_private and e.chat_id != e.sender_id:
            text += f"\n👤 Other User ID: {e.chat_id}"

        # ↩️ REPLY CASE
        if e.is_reply:
            reply = await e.get_reply_message()

            if reply.sender_id:
                text += f"\n↩️ Replied User ID: {reply.sender_id}"
            elif reply.sender_chat:
                text += f"\n↩️ Replied Channel ID: {reply.sender_chat.id}"

        msg = await bot.send_message(e.chat_id, text)

        # auto delete result
        await asyncio.sleep(15)
        try:
            await msg.delete()
        except:
            pass

    except Exception as ex:
        await log_error(bot, "id.py", ex)

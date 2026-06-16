import os
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
    "sender",
    "<b>📤 File Downloader</b>\n\n"
    "<b>Command:</b>\n"
    "• <code>.get &lt;path&gt;</code>\n\n"
    "<b>Usage:</b>\n"
    "Railway server se koi bhi file download karne ke liye.\n"
    "Example: <code>.get plugins/deleter.py</code>"
)

@bot.on(events.NewMessage(pattern=r"\.get\s+(.*)"))
async def send_file_to_user(e):
    if not is_owner(e):
        return

    path = e.pattern_match.group(1).strip()

    if not os.path.exists(path):
        res = await e.edit(f"❌ <b>File not found:</b> <code>{path}</code>", parse_mode="html")
        await asyncio.sleep(10)
        return await res.delete()

    msg = await e.edit(f"📦 <b>Fetching:</b> <code>{path}</code>...", parse_mode="html")

    try:
        # File ko as a Document bhej rahe hain
        await bot.send_file(
            e.chat_id,
            path,
            caption=f"📄 <b>File:</b> <code>{path}</code>",
            parse_mode="html"
        )
        await msg.delete() # Processing message delete kar dete hain

    except Exception:
        await log_error(bot, "sender.py")
        await msg.edit("⚠️ <b>Download Failed!</b> Check logs.", parse_mode="html")

print("✔ sender.py loaded")
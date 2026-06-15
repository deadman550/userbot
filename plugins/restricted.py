# plugins/restricted.py

import os
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "restricted.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print(f"✔ {PLUGIN_NAME} loaded")


# =====================
# TARGET PARSER
# =====================
def parse_target(raw: str):
    raw = raw.strip()
    if raw.lstrip("-").isdigit():
        return int(raw)
    return raw


# =====================
# SAVE RESTRICTED CONTENT
# =====================
@bot.on(events.NewMessage(pattern=r"\.save(?:\s+(.*))?$"))
async def save_restricted(e):
    # Sirf owner ke messages aur replies par kaam karega
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        raw = e.pattern_match.group(1)
        # Agar koi target nahi diya, toh default "Saved Messages" ("me") mein jayega
        target = parse_target(raw) if raw else "me"

        reply = await e.get_reply_message()
        
        # Agar message mein na text hai na media, toh ignore karo
        if not reply.text and not reply.media:
            return

        status = await bot.send_message(e.chat_id, "⏳ `Extracting restricted content...`")

        # CASE 1: Agar message mein Photo/Video/Document hai
        if reply.media:
            # Media download karo (Telethon directly restricted media ko download kar sakta hai)
            file_path = await bot.download_media(reply)
            
            # Target chat mein naya message bankar send karo
            await bot.send_file(
                target, 
                file_path, 
                caption=reply.text
            )
            
            # Storage bachane ke liye local file ko delete kar do
            if os.path.exists(file_path):
                os.remove(file_path)
                
        # CASE 2: Agar message sirf Text hai
        else:
            await bot.send_message(target, reply.text)

        # Success message
        await status.edit("✅ `Restricted content successfully copied!`")
        await asyncio.sleep(3)
        await status.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
        
        # Error aane par user ko batao
        err_msg = await bot.send_message(e.chat_id, f"❌ **Error:** `{str(ex)}`")
        await asyncio.sleep(5)
        await err_msg.delete()

import os
import asyncio
from telethon import events
from telethon.tl.functions.messages import GetAllStickersRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "sticker_backup.py"

print(f"✔ {PLUGIN_NAME} loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "sticker_backup",
    ".stickerbackup\n\n"
    "• Backup all your installed sticker packs\n"
    "• Generates a .txt file with direct links\n"
    "• Owner only"
)

# =====================
# STICKER BACKUP COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.stickerbackup$"))
async def sticker_backup_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        
        # Professional loading status
        status_msg = await bot.send_message(e.chat_id, "⏳ **Fetching installed sticker packs... Please wait.**")

        # Telegram API call to get all installed sticker sets
        result = await bot(GetAllStickersRequest(hash=0))
        
        if not result.sets:
            await status_msg.edit("❌ **Aapke account me koi sticker pack install nahi hai.**")
            await asyncio.sleep(5)
            await status_msg.delete()
            return

        # Prepare text content
        backup_text = "📁 TELEGRAM STICKER PACKS BACKUP\n"
        backup_text += "="*40 + "\n\n"

        for sticker_set in result.sets:
            title = sticker_set.title
            short_name = sticker_set.short_name
            link = f"https://t.me/addstickers/{short_name}"
            backup_text += f"🏷 Name: {title}\n🔗 Link: {link}\n\n"

        # Save to a text file
        file_name = "Sticker_Backup.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(backup_text)

        total_packs = len(result.sets)
        
        caption = (
            "📦 **Sticker Backup Successful!**\n\n"
            f"📊 **Total Packs Found:** `{total_packs}`\n"
            "💡 *Is file ko safe rakhein. Future me dusre account par in links par click karke aap ek second me sticker packs wapas add kar payenge.*"
        )

        # Send the file to the current chat
        await bot.send_file(
            e.chat_id, 
            file_name, 
            caption=caption
        )
        
        # Cleanup
        await status_msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as ex:
        # Emergency file cleanup in case of error
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)
            
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

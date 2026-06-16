import os
import shutil
import asyncio
from datetime import datetime
from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "backup",
    "<b>📦 Full Repo Backup</b>\n\n"
    "<b>Command:</b>\n"
    "• <code>.backup</code>\n\n"
    "<b>Usage:</b>\n"
    "Railway server se pure bot ka code + assets zip karke download karne ke liye."
)

@bot.on(events.NewMessage(pattern=r"\.backup$"))
async def full_backup(e):
    if not is_owner(e):
        return

    status = await e.edit("🗜️ <b>Zipping entire repository (including assets)...</b>", parse_mode="html")
    zip_name = f"bot_full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Ab assets folder is list mein nahi hai, toh wo zip mein aayega
        ignore_list = shutil.ignore_patterns(
            '.git', '__pycache__', 'node_modules', 
            '*.session*', '.venv', 'temp_backup'
        )
        
        temp_dir = "temp_backup"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        # Copying full directory
        shutil.copytree(".", temp_dir, ignore=ignore_list)
        
        # Zip creation
        shutil.make_archive(zip_name, 'zip', temp_dir)
        full_zip_name = zip_name + ".zip"
        
        # File size check (Optional info)
        file_size = os.path.getsize(full_zip_name) / (1024 * 1024) # MB mein
        
        await status.edit(f"📤 <b>Uploading backup ({file_size:.2f} MB)...</b>", parse_mode="html")
        
        await bot.send_file(
            e.chat_id,
            full_zip_name,
            caption=(
                f"✅ <b>Full Backup Successful!</b>\n"
                f"📂 <b>Includes:</b> Code + Assets\n"
                f"📅 <b>Date:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
            ),
            parse_mode="html"
        )
        
        # === CLEANUP ===
        os.remove(full_zip_name)
        shutil.rmtree(temp_dir)
        await status.delete()

    except Exception:
        await log_error(bot, "backup.py")
        await status.edit("⚠️ <b>Backup Failed!</b> Check logs.", parse_mode="html")

print("✔ backup.py loaded")

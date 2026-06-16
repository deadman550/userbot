import os
import shutil
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "rename.py"

print(f"✔ {PLUGIN_NAME} loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "rename",
    ".rename <old_name> | <new_name>\n\n"
    "• Rename any file or folder safely\n"
    "• Use '|' to separate old and new names\n"
    "• Owner only"
)

# =====================
# RENAME COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.rename\s+(?P<args>.+)"))
async def rename_cmd(e):
    if not is_owner(e):
        return

    args = e.pattern_match.group("args")
    
    if "|" not in args:
        await e.delete()
        err_msg = await bot.send_message(
            e.chat_id, 
            "ℹ **Usage:** `.rename old_folder | new_folder`\n*Tip: Names ke beech mein '|' lagana zaruri hai.*"
        )
        await asyncio.sleep(6)
        await err_msg.delete()
        return

    old_name, new_name = [name.strip() for name in args.split("|", 1)]

    try:
        await e.delete()
        status_msg = await bot.send_message(e.chat_id, "⚡ **Renaming...**")

        # Check 1: Kya purana folder exist karta hai?
        if not os.path.exists(old_name):
            await status_msg.edit(f"❌ **Error:** Folder ya file `{old_name}` server par nahi mila.")
            await asyncio.sleep(6)
            await status_msg.delete()
            return

        # Check 2: Kya naya folder pehle se bana hua hai? (To avoid conflict)
        if os.path.exists(new_name):
            await status_msg.edit(f"⚠️ **Error:** Naya naam `{new_name}` ki file/folder pehle se exist karti hai! Kripya dusra naam chunein.")
            await asyncio.sleep(8)
            await status_msg.delete()
            return

        # Shutil move is safer for folders
        shutil.move(old_name, new_name)
        
        await status_msg.edit(f"✅ **Success!**\n\n📁 **Old Name:** `{old_name}`\n🆕 **New Name:** `{new_name}`")
        await asyncio.sleep(10)
        await status_msg.delete()

    except Exception as ex:
        # Error aane par SABSE PEHLE message edit karein, taaki stuck na ho
        try:
            if 'status_msg' in locals():
                await status_msg.edit(f"⚠️ **System Error:** `{str(ex)}`\n\n*Check permissions or if the folder is in use.*")
                await asyncio.sleep(10)
                await status_msg.delete()
        except Exception:
            pass
            
        # Uske baad background me error log karein
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
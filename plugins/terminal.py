import os
import asyncio
from telethon import events
from userbot import bot
from utils.owner import is_owner

# Base Directory (Jahan aapka bot run ho raha hai)
BASE_DIR = os.getcwd()

@bot.on(events.NewMessage(pattern=r"\.put\s+(.*)"))
async def upload_to_repo(e):
    if not is_owner(e):
        return

    path_suffix = e.pattern_match.group(1).strip()
    full_path = os.path.join(BASE_DIR, path_suffix)

    try:
        # CASE 1: AGAR REPLY ME MEDIA HAI (GIF/MP4/Image)
        if e.is_reply:
            reply = await e.get_reply_message()
            if reply.media:
                msg = await e.edit(f"⏳ Uploading media to `{path_suffix}`...")
                await bot.download_media(reply, file=full_path)
                await msg.edit(f"✅ Saved media at: `{path_suffix}`")
                return

            # CASE 2: AGAR REPLY ME SIRF TEXT HAI (New Plugin Code)
            elif reply.text:
                msg = await e.edit(f"⏳ Saving code to `{path_suffix}`...")
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(reply.text)
                await msg.edit(f"✅ File created: `{path_suffix}`\n\n*Note: Restart required to load plugins.*")
                return

        await e.edit("❌ Please reply to a message/media with `.put path/to/file.py`")

    except Exception as ex:
        await e.edit(f"⚠️ Error: {str(ex)}")

# ==========================================
# AUTO-IMPORT LOGIC (MAIN FILE MODIFIER)
# ==========================================
@bot.on(events.NewMessage(pattern=r"\.addimport\s+(.*)"))
async def add_import(e):
    if not is_owner(e):
        return
    
    module_name = e.pattern_match.group(1).strip()
    main_file = "main.py" # Aapki main file ka naam
    
    try:
        with open(main_file, "r") as f:
            lines = f.readlines()
        
        new_import = f"import {module_name}\n"
        
        if new_import in lines:
            return await e.edit(f"ℹ️ `{module_name}` is already imported.")
            
        lines.insert(0, new_import) # Top par add karega
        
        with open(main_file, "w") as f:
            f.writelines(lines)
            
        await e.edit(f"✅ Added `import {module_name}` to `{main_file}`. Restarting...")
        # Optional: Auto-restart logic yahan add kar sakte hain
    except Exception as ex:
        await e.edit(f"⚠️ Failed to modify main file: {ex}")

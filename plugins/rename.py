import os
from telethon import events
from userbot import bot
from utils.owner import is_owner

@bot.on(events.NewMessage(pattern=r"\.rename\s+(.*)\s+(.*)"))
async def rename_folder(e):
    if not is_owner(e):
        return
    
    old_name = e.pattern_match.group(1).strip()
    new_name = e.pattern_match.group(2).strip()

    try:
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            await e.edit(f"✅ Renamed `{old_name}` to `{new_name}` successfully!")
        else:
            await e.edit(f"❌ Folder `{old_name}` nahi mila.")
    except Exception as ex:
        await e.edit(f"⚠️ Error: {str(ex)}")

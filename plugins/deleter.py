import os
import shutil
from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "deleter",
    "<b>🗑️ Deleter Plugin</b>\n\n"
    "<b>Commands:</b>\n"
    "• <code>.del &lt;path&gt;</code>\n\n"
    "<b>Usage:</b>\n"
    "Apne repository se kisi bhi file ya folder ko delete karne ke liye.\n"
    "Example: <code>.del plugins/temp.py</code>\n\n"
    "⚠️ <i>Warning: Action cannot be undone!</i>"
)

@bot.on(events.NewMessage(pattern=r"\.del\s+(.*)"))
async def delete_item(e):
    if not is_owner(e):
        return

    path_to_delete = e.pattern_match.group(1).strip()
    
    # 🔒 SECURITY CHECK: Main files ko protect karne ke liye
    protected = ["main.py", "loader.py", "session", ".env", "config"]
    if any(x in path_to_delete.lower() for x in protected):
        return await e.edit(
            "🛡️ <b>Security Alert:</b> System files ko delete karna allow nahi hai.",
            parse_mode="html"
        )

    if not os.path.exists(path_to_delete):
        return await e.edit(
            f"🔍 <b>Path not found:</b> <code>{path_to_delete}</code>",
            parse_mode="html"
        )

    try:
        if os.path.isfile(path_to_delete):
            os.remove(path_to_delete)
            await e.edit(
                f"🗑️ <b>File Removed:</b> <code>{path_to_delete}</code>",
                parse_mode="html"
            )
        
        elif os.path.isdir(path_to_delete):
            shutil.rmtree(path_to_delete)
            await e.edit(
                f"📂 <b>Folder Purged:</b> <code>{path_to_delete}</code>",
                parse_mode="html"
            )
            
    except Exception:
        await log_error(bot, "deleter.py")
        await e.edit(
            "⚠️ <b>Delete Failed:</b> Check logs for details.",
            parse_mode="html"
        )

print("✔ deleter.py loaded")
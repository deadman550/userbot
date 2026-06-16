import os
import asyncio
from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "tree",
    "<b>📂 Tree Explorer</b>\n\n"
    "<b>Command:</b>\n"
    "• <code>.tree</code>\n\n"
    "<b>Usage:</b>\n"
    "Bot ki puri directory structure dekhne ke liye.\n"
    "⏱️ <i>Auto-delete after 50s.</i>"
)

@bot.on(events.NewMessage(pattern=r"\.tree$"))
async def tree_view(e):
    if not is_owner(e):
        return

    # Mapping start karte waqt HTML mode on rakha hai
    msg = await e.edit("🌳 <b>Mapping directory structure...</b>", parse_mode="html")
    
    output = "<b>📁 Project Root</b>\n"
    
    # Ye function directory scan karega
    for root, dirs, files in os.walk("."):
        # Hidden folders aur unwanted files skip karein
        if any(x in root for x in [".git", "__pycache__", "session", "assets"]):
            continue
            
        level = root.replace(".", "").count(os.sep)
        indent = "   " * level
        folder_name = os.path.basename(root)
        
        if folder_name:
            output += f"{indent}┣ <b>{folder_name}/</b>\n"
        
        sub_indent = "   " * (level + 1)
        for f in files:
            if f.endswith((".py", ".env", ".json", ".txt")):
                output += f"{sub_indent}┗ <code>{f}</code>\n"
        
        # Message bohot bada na ho jaye (Telegram limit 4096)
        if len(output) > 3500:
            output += "<i>...and more files (Limit reached)</i>"
            break

    # Final output with HTML parsing
    final_msg = await msg.edit(output, parse_mode="html")

    # === 50 SECONDS AUTO DELETE ===
    await asyncio.sleep(50)
    try:
        await final_msg.delete()
    except Exception:
        pass

print("✔ tree.py loaded")

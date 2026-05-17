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
    "grep",
    "<b>🔍 Code Searcher (Grep)</b>\n\n"
    "<b>Command:</b>\n"
    "• <code>.find &lt;text&gt;</code>\n\n"
    "<b>Usage:</b>\n"
    "Pure bot ke code mein koi bhi word ya function dhundne ke liye.\n"
    "Example: <code>.find register_help</code>\n\n"
    "⏱️ <i>Results delete automatically after 60s.</i>"
)

@bot.on(events.NewMessage(pattern=r"\.find\s+(.*)"))
async def grep_search(e):
    if not is_owner(e):
        return

    query = e.pattern_match.group(1).strip()
    if len(query) < 3:
        res = await e.edit("⚠️ <b>Search query kam se kam 3 characters ki honi chahiye!</b>", parse_mode="html")
        await asyncio.sleep(10)
        return await res.delete()

    msg = await e.edit(f"🔍 <b>Searching for:</b> <code>{query}</code>...", parse_mode="html")
    
    results = []
    # In folders ko skip karenge (Security + Speed)
    skip_dirs = [".git", "__pycache__", "session", "assets"]

    for root, dirs, files in os.walk("."):
        # Skip logic
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith((".py", ".txt", ".json", ".env")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                # Clean path for display
                                display_path = file_path.replace("./", "")
                                results.append(f"📍 <code>{display_path}</code> [L:{line_num}]")
                except Exception:
                    continue

    if not results:
        res = await msg.edit(f"❌ <b>'{query}'</b> kahin nahi mila.", parse_mode="html")
        await asyncio.sleep(10)
        return await res.delete()
    else:
        output = f"🔍 <b>Search Results for:</b> <code>{query}</code>\n\n"
        output += "\n".join(results[:15]) # Limit to 15 results to avoid long message
        
        if len(results) > 15:
            output += f"\n\n<i>...and {len(results)-15} more matches.</i>"
            
        final_msg = await msg.edit(output, parse_mode="html")
        
        # === 60 SECONDS AUTO DELETE ===
        await asyncio.sleep(60)
        try:
            await final_msg.delete()
        except Exception:
            pass

print("✔ grep.py loaded")

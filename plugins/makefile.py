import os
import asyncio
import zipfile
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "makefile.py"

print(f"✔ {PLUGIN_NAME} loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "makefile",
    ".makefile <filename.ext>\n\n"
    "• Convert replied text into any file (.py, .txt, .zip, etc.)\n"
    "• Must reply to a text message\n"
    "• Owner only"
)

# =====================
# MAKE FILE COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.makefile\s+(?P<filename>\S+)"))
async def makefile_cmd(e):
    if not is_owner(e):
        return

    # Check if it's a reply to a message
    if not e.is_reply:
        await e.delete()
        err_msg = await bot.send_message(e.chat_id, "❌ **Error:** Khas taur par kisi text message par reply karke yeh command use karein!")
        await asyncio.sleep(4)
        await err_msg.delete()
        return

    filename = e.pattern_match.group("filename").strip()

    try:
        # Delete trigger message for clean look
        await e.delete()
        
        # Professional loading status
        status_msg = await bot.send_message(e.chat_id, "⚡ **Creating file... Please wait.**")

        # Get replied message text
        reply_msg = await e.get_reply_message()
        content = reply_msg.text

        if not content:
            await status_msg.edit("❌ **Error:** Replied message me koi text nahi mila!")
            await asyncio.sleep(4)
            await status_msg.delete()
            return

        # SMART ZIP HANDLING: Agar user .zip file chahta hai
        if filename.endswith(".zip"):
            base_name = filename.rsplit('.', 1)[0]
            # Content ke hisab se inner file ka extension auto-detect karna
            inner_ext = ".py" if "import " in content or "def " in content else ".txt"
            inner_filename = f"{base_name}{inner_ext}"
            
            # Zip archive create karna aur usme text write karna
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr(inner_filename, content)
        else:
            # Baaki sabhi normal files ke liye (py, txt, html etc.)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

        # Telegram par file send karna (jis message par reply kiya tha uske niche hi aayega)
        await bot.send_file(
            e.chat_id,
            filename,
            caption=f"📁 **File Name:** `{filename}`\n✨ **Generated Successfully!**",
            reply_to=reply_msg.id
        )

        # Storage clean karne ke liye local file delete karna
        if os.path.exists(filename):
            os.remove(filename)

        # Loading status message delete karna
        await status_msg.delete()

    except Exception as ex:
        # Kisi error ke case me temporary file delete karna safe rakhne ke liye
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)
            
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
        
import traceback
from datetime import datetime

async def log_error(bot, plugin):
    text = (
        "❌ **Userbot Error**\n\n"
        f"🧩 Plugin: `{plugin}`\n"
        f"🕒 Time: `{datetime.now()}`\n\n"
        "```"
        f"{traceback.format_exc()}"
        "```"
    )
    await bot.send_message("me", text)
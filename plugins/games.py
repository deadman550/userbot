import random
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("games.py")
print("✔ games.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "games",
    ".dice\n"
    ".coin\n"
    ".luck\n"
    ".rate\n"
    ".roll NUMBER\n\n"
    "Fun random games\n"
    "• Owner only\n"
    "• Auto delete output"
)

# =====================
# GAMES HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.(dice|coin|luck|rate|roll)(?:\s+(.*))?$"))
async def games_handler(e):
    if not is_owner(e):
        return

    try:
        cmd = e.pattern_match.group(1)
        arg = e.pattern_match.group(2)

        # delete command safely
        try:
            await e.delete()
        except:
            pass

        if cmd == "dice":
            text = f"🎲 Dice: {random.randint(1, 6)}"

        elif cmd == "coin":
            text = f"🪙 Coin: {random.choice(['Head', 'Tail'])}"

        elif cmd == "luck":
            text = f"🍀 Luck: {random.randint(0, 100)}%"

        elif cmd == "rate":
            text = f"⭐ Rating: {random.randint(0, 10)}/10"

        elif cmd == "roll":
            if arg and arg.isdigit() and int(arg) > 0:
                num = int(arg)
            else:
                num = 100
            text = f"🎯 Rolled: {random.randint(1, num)}"

        else:
            return

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error("games.py", ex)
        await log_error(bot, "games.py", ex)

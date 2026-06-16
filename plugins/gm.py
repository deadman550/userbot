# =====================
# GOOD MORNING ART
# =====================

from telethon import events
from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "gm.py"

print("✔ gm.py loaded")

@bot.on(events.NewMessage(pattern=r"\.gm$"))
async def good_morning(e):
    text = (
        "^_^)\n"
        ".................^v^\n"
        "⋱ ⋮ ⋰\n"
        "⋯ ◯ ⋯¨. ︵ ..............................................^v^\n"
        "¨︵¸︵( ░░ )︵.︵.︵..............^v^\n"
        "... (´░░░░░░ ') ░░░' )\n"
        "´︶´¯︶´︶´︶´︶.....^v^..........^v^\n"
        "....^v^....▄▀▀──▄▀▀▄─▄▀▀▄─█▀▄....^v^....\n"
        "....^v^....█─▀█─█──█─█──█─█─█....^v^....\n"
        "....^v^....─▀▀───▀▀───▀▀──▀▀─....^v^....\n"
        "....^v^........^v^........^v^........^v^........^v^....\n"
        "█▄─▄█─▄▀▀▄─█▀▄─█▄─█─█─█▄─█─▄▀▀─\n"
        "█─▀─█─█──█─██▀─█─▀█─█─█─▀█─█─▀█\n"
        "▀───▀──▀▀──▀─▀─▀──▀─▀─▀──▀──▀▀─"
    )

    await e.edit(text)


# =====================
# HELP
# =====================
register_help(
    "gm",
    ".gm\n\n"
    "• Sends Good Morning ASCII art\n"
    "• No auto delete"
)

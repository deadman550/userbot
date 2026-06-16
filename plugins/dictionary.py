# Dictionary & Urban Dictionary Plugin
# Lightweight – Telethon Userbot Compatible

import requests
from telethon import events
from PyDictionary import PyDictionary

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "dictionary.py"
print("✔ dictionary.py loaded (Urban + Dictionary)")


# =====================
# URBAN DICTIONARY
# =====================
@bot.on(events.NewMessage(pattern=r"\.ud\s+(.+)"))
async def urban_dict(e):
    try:
        word = e.pattern_match.group(1)
        await e.edit("🔍 Searching Urban Dictionary...")

        url = f"https://api.urbandictionary.com/v0/define?term={word}"
        res = requests.get(url).json()

        if not res["list"]:
            return await e.edit("❌ No results found.")

        data = res["list"][0]
        meaning = data["definition"]
        example = data["example"]

        text = (
            f"📘 **Urban Dictionary**\n\n"
            f"**Word:** `{word}`\n\n"
            f"**Meaning:**\n`{meaning}`\n\n"
            f"**Example:**\n`{example}`"
        )

        await e.edit(text)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        await e.edit("❌ Urban Dictionary API error.")
        mark_plugin_error(PLUGIN_NAME)


# =====================
# NORMAL DICTIONARY
# =====================
@bot.on(events.NewMessage(pattern=r"\.meaning\s+(.+)"))
async def normal_dict(e):
    try:
        word = e.pattern_match.group(1)
        await e.edit("📖 Searching dictionary...")

        dictionary = PyDictionary()
        result = dictionary.meaning(word)

        if not result:
            return await e.edit(f"❌ No meaning found for `{word}`.")

        output = f"📗 **Dictionary Meaning**\n\n**Word:** `{word}`\n\n"

        for part, meanings in result.items():
            output += f"**{part}**\n"
            for m in meanings:
                output += f"• `{m}`\n"
            output += "\n"

        await e.edit(output)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        await e.edit(f"❌ Couldn't fetch meaning for `{word}`.")
        mark_plugin_error(PLUGIN_NAME)


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "dictionary",
    ".ud <word>\n"
    ".meaning <word>\n\n"
    "• Urban Dictionary slang meanings\n"
    "• Normal English dictionary meanings\n"
    "• Lightweight & safe"
)
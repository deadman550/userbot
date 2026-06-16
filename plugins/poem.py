import asyncio
import random
from telethon import events
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

from userbot import bot
from utils.help_registry import register_help

PLUGIN_NAME = "poem.py"
print("✔ poem.py loaded (RANDOM FUN POEMS)")

DEFAULTUSER = "ULTROID USER"

POEMS = [
    "Roses are red 🌹\n"
    "Violets are blue 💙\n"
    "Life is confusing\n"
    "And so are you 😌",

    "Roses are red 🌹\n"
    "Dreams feel near ✨\n"
    "I’ll start tomorrow\n"
    "That’s been my year 😅",

    "Roses are red 🌹\n"
    "Violets are blue 💙\n"
    "I respect everyone\n"
    "But not people like you 😏",

    "Roses are red 🌹\n"
    "Night feels long 🌙\n"
    "I pretend I’m strong\n"
    "But everything feels wrong 😞",

    "Roses are red 🌹\n"
    "Coffee is brown ☕\n"
    "Mondays are evil\n"
    "But we still get around 😴",

    "Roses are red 🌹\n"
    "Sky is wide 🌌\n"
    "I had motivation\n"
    "But it suddenly died 💀",

    "I talk less now 🤍\n"
    "Not because I’m okay\n"
    "Because explaining pain\n"
    "Never changes a thing 😞",

    "Roses are red 🌹\n"
    "Night feels deep 🌙\n"
    "I planned to work\n"
    "But chose to sleep 😴",

    "Roses are red 🌹\n"
    "Hope is bright ✨\n"
    "Trust the process\n"
    "You’ll be alright 💪",

    "Roses are red 🌹\n"
    "Phone is my fate 📱\n"
    "I came to study\n"
    "But started to scroll… again 😭",
]

@bot.on(events.NewMessage(pattern=r"\.poem$"))
async def random_poem(e):
    poem = random.choice(POEMS)

    await e.edit("✍️ Writing a poem...")
    await asyncio.sleep(2)

    owner = await e.get_sender()
    owner_name = owner.first_name or "Owner"
    owner_id = owner.id

    signature = f"✍️ [{owner_name}](tg://user?id={owner_id})"

    # Ultroid-style reply logic
    if e.is_reply:
        r = await e.get_reply_message()
        if r and r.sender:
            user_name = r.sender.first_name or "User"
            user_id = r.sender.id
            signature = (
                f"✍️ [{owner_name}](tg://user?id={owner_id})"
                f" → [{user_name}](tg://user?id={user_id})"
            )

    await e.edit(
        f"{poem}\n\n{signature}",
        link_preview=False
    )

# =====================
# HELP
# =====================
register_help(
    "poems",
    ".poem (reply optional)\n\n"
    "• Random fun poem\n"
    "• Reply user name auto detected\n"
    "• Safe content"
)

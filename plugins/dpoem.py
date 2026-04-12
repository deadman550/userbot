# Made By @Senku_Ishigamiii (SAFE VERSION)
# Converted for Telethon Userbot

import asyncio
import random
from telethon import events
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
  
from userbot import bot
from utils.help_registry import register_help

PLUGIN_NAME = "dpoem.py"
print("✔ dpoem.py loaded (RANDOM DARK POEMS)")

DEFAULTUSER = "Detor"

POEMS = [
    "Roses are red 🌹\n"
    "Violets are blue 💙\n"
    "my superpower is\n"
    "I can cum on you",

    "Roses are red 🌹\n"
    "Coffee is brown ☕\n"
    "when you kissed me\n"
    "I immediately grew",
  
    "Roses are red 🌹\n"
    "Violets are blue\n"
    "should have turned on the light\n"
    "now my child will moo.",

    "Roses are red 🌹\n"
    "Violets are blue\n"
    "Now that I've cum\n"
    "I bid you adieu",

    "Roses are red 🌹\n"
    "Violets are blue\n"
    "i do only anal\n"
    "I thought you knew",

    "Roses are red 🌹\n"
    "Violets are blue\n"
    "Can i fill you up\n"
    "with my special fondue?",

    "Roses are red\n"
    "Violets are blue\n"
    "in my pants\n"
    "I'm hiding a statue",

    "Roses are red\n"
    "Violets are blue\n"
    "if I said you're pretty\n"
    "would you touch my bamboo?",

    "Roses are red\n"
    "Violets are blue\n"
    "I’ve got five fingers\n"
    "Guess which one is for you?",
]

@bot.on(events.NewMessage(pattern=r"\.dpoem$"))
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
    "dpoem",
    ".dpoem (reply optional)\n\n"
    "• Random fun poem\n"
    "• Reply user name auto detected\n"
    "• Safe content"
  )

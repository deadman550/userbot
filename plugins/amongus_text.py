# Among Us – Text Only (Lightweight & Fun)
# Telethon Userbot Compatible

import asyncio
from telethon import events
from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded

PLUGIN_NAME = "amongus_text.py"
print("✔ amongus_text.py loaded (Among Us Text Only)")


async def eject_animation(e):
    frames = [
        "ඞ",
        "ㅤඞ",
        "ㅤㅤඞ",
        "ㅤㅤㅤඞ",
        "ㅤㅤㅤㅤඞ",
        "ㅤㅤㅤㅤㅤඞ",
        "ㅤㅤㅤㅤㅤㅤඞ",
        "ㅤㅤㅤㅤㅤㅤㅤඞ",
        "ㅤㅤㅤㅤㅤㅤㅤㅤඞ",
        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ",
    ]
    for f in frames:
        await e.edit(f)
        await asyncio.sleep(0.4)


@bot.on(events.NewMessage(pattern=r"\.timp\s+(.+)"))
async def imposter_yes(e):
    name = e.pattern_match.group(1)

    await e.edit("📢 **Emergency Meeting Called!**")
    await asyncio.sleep(2)

    await e.edit("🗣️ **Crewmates:** Something is sus...")
    await asyncio.sleep(2)

    await e.edit(f"👀 **Crewmates:** I saw **{name}** near the vent!")
    await asyncio.sleep(2)

    await e.edit(f"🗳️ **Voting...**\nEveryone voted **{name}**")
    await asyncio.sleep(2)

    await e.edit(f"🚀 **{name} is ejected...**")
    await asyncio.sleep(1)

    await eject_animation(e)

    await e.edit(
        f"""
. 　　　。　　　　•　 　ﾟ　　。
 .　　　 　　.　　　　　。　　 。　.
 
  . 　　 。   　     ඞ         。 . 　　 •
 
  ﾟ **{name} was an Impostor.**
  
      🔴 **0 Impostors remain**
        """
    )
    await asyncio.sleep(4)
    await e.delete()


@bot.on(events.NewMessage(pattern=r"\.timpn\s+(.+)"))
async def imposter_no(e):
    name = e.pattern_match.group(1)

    await e.edit("📢 **Emergency Meeting Called!**")
    await asyncio.sleep(2)

    await e.edit("🗣️ **Crewmates:** Something feels off...")
    await asyncio.sleep(2)

    await e.edit(f"🤔 **Crewmates:** Maybe it’s **{name}?**")
    await asyncio.sleep(2)

    await e.edit(f"🗳️ **Voting...**\nEveryone voted **{name}**")
    await asyncio.sleep(2)

    await e.edit(f"🚀 **{name} is ejected...**")
    await asyncio.sleep(1)

    await eject_animation(e)

    await e.edit(
        f"""
. 　　　。　　　　•　 　ﾟ　　。
 .　　　 　　.　　　　　。　　 。　.
 
  . 　　 。   　     ඞ         。 . 　　 •
 
  ﾟ **{name} was NOT an Impostor.**
  
      🟡 **1 Impostor remains**
        """
    )
    await asyncio.sleep(4)
    await e.delete()


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "amongus_text",
    ".timp <name>\n"
    ".timpn <name>\n\n"
    "• Among Us text-only animation\n"
    "• Lightweight & fun\n"
    "• No stickers or images"
)
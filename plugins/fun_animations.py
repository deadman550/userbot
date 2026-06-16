import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun_animations.py"
print("✔ fun_animations.py loaded (FUN v1)")

# =====================
# HELP
# =====================
register_help(
    "funanimation",
    ".policethief\n"
    ".reality (reply)\n"
    ".experiment (reply)\n\n"
    "• Fun animations\n"
    "• Auto delete enabled\n"
    "• Reply based where required"
)

# =====================
# POLICE × THIEF
# =====================
@bot.on(events.NewMessage(pattern=r"\.policethief$"))
async def police_thief(e):
    try:
        msg = await e.respond("🚨 Police on duty...")
        frames = [
            "🧍‍♂️💰  : Hehe paisa 💸",

            "🧍‍♂️💰  : Hehe paisa 💸\n"
            
            "👮‍♂️     : OYE RUK 😡\n"

            "🏃‍♂️💰  : Pakad ke dikha 😜\n"
            
            "🚓💨     : WEEE-OOO 🚨\n"

            "😨🏃‍♂️  : Sir maaf karo 😭\n"
            "👮‍♂️🤝  : Chal thane 😈",

            "🚔 **CASE CLOSED ✅**"
        ]

        for f in frames:
            await asyncio.sleep(1.3)
            await msg.edit(f)

        await asyncio.sleep(4)
        await msg.delete()

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# REALITY (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.reality$"))
async def reality(e):
    try:
        if not e.is_reply:
            return await e.reply("Reply to a message.")

        msg = await e.reply(
            "📱 **Instagram Life**\n"
            "💸 Rich\n"
            "😎 Cool\n"
            "🔥 Perfect\n\n"
            "📉 **Reality**\n"
            "💀 No money\n"
            "😴 Sleepy\n"
            "📱 Phone only"
        )

        await asyncio.sleep(4)
        await msg.delete()

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# EXPERIMENT (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.experiment$"))
async def experiment(e):
    try:
        if not e.is_reply:
            return await e.reply("Reply to a message.")

        msg = await e.reply(
            "🧪 **Mixing stupidity…**\n\n"
            "⚠️ Warning\n"
            "💥 Reaction unstable\n"
            "🤯 Result: **YOU**"
        )

        await asyncio.sleep(4)
        await msg.delete()

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

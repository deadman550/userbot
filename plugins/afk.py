import asyncio
from datetime import datetime

from telethon import events
from userbot import bot
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.help_registry import register_help

PLUGIN_NAME = "afk.py"
print("✔ afk.py loaded (SMART AFK + AUTO OFF)")
# =====================
# GLOBAL STATE
# =====================
AFK = {
    "on": False,
    "since": None,
    "reason": None,
}

# uid -> last reply timestamp
REPLIED = {}

AFK_COOLDOWN = 10 * 60  # 10 minutes


# =====================
# TIME FORMATTER
# =====================
def format_afk_time(since):
    delta = datetime.utcnow() - since
    total = int(delta.total_seconds())

    hours = total // 3600
    minutes = (total % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


# =====================
# AFK ON
# =====================
@bot.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?$"))
async def afk_on(e):
    AFK["on"] = True
    AFK["since"] = datetime.utcnow()
    AFK["reason"] = e.pattern_match.group(1) or "AFK"
    REPLIED.clear()

    await e.edit(
        "😴 **AFK enabled**\n"
        f"Reason: `{AFK['reason']}`"
    )


# =====================
# AUTO OFF (OWNER MESSAGE)
# =====================
@bot.on(events.NewMessage(outgoing=True))
async def afk_auto_off(e):
    if not AFK["on"]:
        return

    if e.raw_text and e.raw_text.startswith(".afk"):
        return

    AFK["on"] = False
    AFK["since"] = None
    AFK["reason"] = None
    REPLIED.clear()

    msg = await e.respond("✅ **AFK disabled (you are back)**")
    await asyncio.sleep(3)
    await msg.delete()


# =====================
# AFK AUTO REPLY (COOLDOWN)
# =====================
@bot.on(events.NewMessage(incoming=True))
async def afk_reply(e):
    try:
        if not AFK["on"]:
            return

        # ignore own msgs
        if e.out:
            return

        # ignore bots
        sender = await e.get_sender()
        if sender and sender.bot:
            return

        # only DM OR mention OR reply
        if not e.is_private and not e.mentioned and not e.is_reply:
            return

        uid = e.sender_id
        now = datetime.utcnow().timestamp()

        last = REPLIED.get(uid)
        if last and (now - last) < AFK_COOLDOWN:
            return

        REPLIED[uid] = now

        away = format_afk_time(AFK["since"])

        text = (
            "😴 **AFK MODE**\n\n"
            f"Reason: `{AFK['reason']}`\n"
            f"Away since: `{away}`\n\n"
            "I’ll reply soon 👋"
        )

        m = await e.reply(text)
        await asyncio.sleep(5)
        await m.delete()

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)


# =====================
# HELP
# =====================
register_help(
    "afk",
    ".afk <reason>\n\n"
    "• Auto AFK off when you send message\n"
    "• Per-user cooldown enabled\n"
    "• No replies to bots\n"
    "• Time shown in hours/minutes"
        )

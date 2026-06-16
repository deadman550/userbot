import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ spam.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "spam",
    ".spam COUNT TEXT\n"
    "exm: .spam 5 hello\n\n"
    ".delayspam COUNT DELAY TEXT\n"
    "exm: .delayspam 5 1.5 hello\n\n"
    ".replyspam COUNT  (reply)\n"
    "exm: reply + .replyspam 10\n\n"
    "• All commands are owner-only\n"
    "• Flood-safe delay applied"
)

# =====================
# SPAM
# =====================
@bot.on(events.NewMessage(pattern=r"\.spam (\d+) (.+)"))
async def spam_cmd(e):
    if not is_owner(e):
        return

    try:
        count = int(e.pattern_match.group(1))
        text = e.pattern_match.group(2)

        try:
            await e.delete()
        except Exception:
            pass

        for _ in range(count):
            await bot.send_message(e.chat_id, text)
            await asyncio.sleep(0.4)

    except Exception:
        await log_error(bot, "spam.py")


# =====================
# DELAY SPAM
# =====================
@bot.on(events.NewMessage(pattern=r"\.delayspam (\d+) ([0-9.]+) (.+)"))
async def delay_spam_cmd(e):
    if not is_owner(e):
        return

    try:
        count = int(e.pattern_match.group(1))
        delay = float(e.pattern_match.group(2))
        text = e.pattern_match.group(3)

        try:
            await e.delete()
        except Exception:
            pass

        for _ in range(count):
            await bot.send_message(e.chat_id, text)
            await asyncio.sleep(delay)

    except Exception:
        await log_error(bot, "spam.py")


# =====================
# REPLY SPAM
# =====================
@bot.on(events.NewMessage(pattern=r"\.replyspam (\d+)"))
async def reply_spam_cmd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        count = int(e.pattern_match.group(1))
        reply = await e.get_reply_message()

        try:
            await e.delete()
        except Exception:
            pass

        text = reply.text or "👀"

        for _ in range(count):
            await bot.send_message(
                e.chat_id,
                text,
                reply_to=reply.id
            )
            await asyncio.sleep(0.4)

    except Exception:
        await log_error(bot, "spam.py")
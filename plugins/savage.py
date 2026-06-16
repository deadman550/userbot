# plugins/savage.py

import random
from telethon import events
from telethon.tl.types import MessageEntityMention

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "savage.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ savage.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "savage",
    ".roast (reply / @mention)\n"
    ".iq (reply / @mention)\n"
    ".future (reply / @mention)\n"
    ".gayrate\n"
    ".ssimp (reply / @mention)\n"
    ".kill (reply / @mention)\n"
    ".punch (reply / @mention)\n"
    ".chaos\n"
    ".cold\n"
    ".hug sad (reply / @mention)\n"
    ".hug angry (reply / @mention)\n\n"
    "• Savage / Fun commands\n"
    "• Owner only\n"
    "• Auto delete enabled"
)

# =====================
# DATA
# =====================
ROASTS = [
    "{t}, tera confidence free trial pe hai 😂",
    "{t}, dimaag loading… please wait ⏳",
    "{t}, error 404: common sense not found 🤡",
    "{t}, zyada bolne se smart nahi ban jaate 😏"
]

HUG_SAD = [
    "🤗 {t} sab thik ho jayega",
    "🫂 {t} stay strong",
    "💙 {t} akela nahi hai tu"
]

HUG_ANGRY = [
    "😤 {t} shaant ho ja",
    "🤝 {t} chill kar bhai",
    "🧊 {t} thoda cold le"
]

FUTURES = [
    "{t} ka future bright hai ✨",
    "{t} startup founder banega 😎",
    "{t} ka future loading… ⏳",
    "{t} ka future risky lag raha 😬"
]

# =====================
# HELPER
# =====================
async def get_target(e):
    # reply based
    if e.is_reply:
        r = await e.get_reply_message()
        if r and r.sender_id:
            name = r.sender.first_name or "User"
            return f"[{name}](tg://user?id={r.sender_id})", r.id

    # @mention based
    if e.message.entities:
        for ent in e.message.entities:
            if isinstance(ent, MessageEntityMention):
                username = e.raw_text[ent.offset: ent.offset + ent.length]
                try:
                    user = await bot.get_entity(username)
                    return f"[{user.first_name}](tg://user?id={user.id})", None
                except:
                    pass

    return None, None

# =====================
# HANDLER
# =====================
@bot.on(events.NewMessage(
    pattern=r"\.(roast|iq|future|gayrate|ssimp|kill|punch|chaos|cold|hug)(?:\s+(sad|angry))?$"
))
async def savage_handler(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        cmd = e.pattern_match.group(1)
        mood = e.pattern_match.group(2)

        target, reply_to = await get_target(e)

        # ---------- LOGIC ----------
        if cmd in ("roast", "iq", "future", "ssimp", "kill", "punch", "hug") and not target:
            return

        if cmd == "roast":
            text = random.choice(ROASTS).format(t=target)

        elif cmd == "iq":
            text = f"🧠 {target} ka IQ hai **{random.randint(40,180)}**"

        elif cmd == "future":
            text = random.choice(FUTURES).format(t=target)

        elif cmd == "gayrate":
            text = f"🏳️‍🌈 Gay meter: **{random.randint(1,100)}%**"

        elif cmd == "ssimp":
            text = f"💘 {target} certified SIMP hai 😂"

        elif cmd == "kill":
            text = f"🔪 {target} ko imaginary slap mila 😈"

        elif cmd == "punch":
            text = f"👊 {target} got punched (virtually 😌)"

        elif cmd == "chaos":
            text = "🔥 CHAOS MODE ACTIVATED 🔥"

        elif cmd == "cold":
            text = "🧊 Cold reply detected"

        elif cmd == "hug":
            if mood == "sad":
                text = random.choice(HUG_SAD).format(t=target)
            elif mood == "angry":
                text = random.choice(HUG_ANGRY).format(t=target)
            else:
                return
        else:
            return

        msg = await bot.send_message(e.chat_id, text, reply_to=reply_to)
        await auto_delete(msg, 6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

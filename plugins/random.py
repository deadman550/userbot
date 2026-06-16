# plugins/random.py

import random
from telethon import events
from telethon.tl.types import MessageEntityMention

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "random.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ random.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "random",
    ".predict | .8ball | .quote | .joke\n"
    ".truth | .dare\n"
    ".insult USER\n"
    ".compliment USER\n"
    ".roast USER\n"
    ".rate USER\n"
    ".iq USER\n"
    ".simp USER\n"
    ".ship (reply / @mention / name / name1 name2)\n\n"
    "• Proper user mention\n"
    "• Group + DM supported\n"
    "• Auto delete enabled\n"
    "• Owner only"
)

# =====================
# DATA
# =====================
DATA = {
    "predict": [
        "Yes 👍", "No ❌", "Maybe 🤔", "Definitely 🔥",
        "Never 💀", "Future looks bright ✨"
    ],
    "8ball": [
        "Ask again later 🎱", "Sure thing 😎",
        "Impossible ❌", "100% confirmed ✅"
    ],
    "quote": [
        "Code > Sleep.",
        "Discipline > Motivation.",
        "Silence is also an answer."
    ],
    "joke": [
        "Debugging is like being a detective in your own crime scene 😂",
        "AI fixes typos, not life 🤡"
    ],
    "truth": [
        "Last lie kya boli thi?",
        "Kisi pe secretly crush hai?"
    ],
    "dare": [
        "Next message ALL CAPS me bhejo 😈",
        "5 min tak online raho bina bole"
    ],
    "insult": [
        "{target}, small brain detected 🧠",
        "{target}, skill issue 😏"
    ],
    "compliment": [
        "{target} is a legend 🔥",
        "{target} has king energy 👑"
    ],
    "roast": [
        "{target}, tera confidence free trial pe hai 😂",
        "{target}, error 404: sense not found 🤡"
    ],
    "simp": [
        "{target} ke liye simping level 💯",
        "{target} ke DM me simp mode ON 😌"
    ]
}

# =====================
# TARGET HELPER
# =====================
async def get_target(e, arg):
    reply_to = None
    target = None

    # reply based
    if e.is_reply:
        r = await e.get_reply_message()
        if r and r.sender_id:
            u = await bot.get_entity(r.sender_id)
            target = f"[{u.first_name or 'User'}](tg://user?id={u.id})"
            reply_to = r.id
            return target, reply_to

    # @mention based
    if e.message.entities:
        for ent in e.message.entities:
            if isinstance(ent, MessageEntityMention):
                username = e.raw_text[ent.offset: ent.offset + ent.length]
                try:
                    u = await bot.get_entity(username)
                    target = f"[{u.first_name or 'User'}](tg://user?id={u.id})"
                    return target, None
                except:
                    pass

    # text based
    if arg:
        return arg, None

    return None, None

# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(
    pattern=r"\.(predict|8ball|quote|joke|truth|dare|insult|compliment|roast|rate|iq|simp|ship)(?:\s+(.*))?$"
))
async def random_handler(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        cmd = e.pattern_match.group(1)
        arg = e.pattern_match.group(2)
        you = f"[You](tg://user?id={e.sender_id})"

        # ================= SHIP =================
        if cmd == "ship":
            percent = random.randint(10, 100)

            if arg and len(arg.split()) == 2:
                a, b = arg.split(None, 1)
                text = f"💖 {a} ❤️ {b}\nCompatibility: **{percent}%**"
            else:
                target, reply_to = await get_target(e, arg)
                if not target:
                    return
                text = f"💖 {target} ❤️ {you}\nCompatibility: **{percent}%**"

            msg = await bot.send_message(e.chat_id, text)
            return await auto_delete(msg, 8)

        # ================= RATE =================
        if cmd == "rate":
            target, reply_to = await get_target(e, arg)
            rate = random.randint(1, 10)
            msg = await bot.send_message(
                e.chat_id,
                f"⭐ {target or 'You'} rating: {rate}/10",
                reply_to=reply_to
            )
            return await auto_delete(msg, 6)

        # ================= IQ =================
        if cmd == "iq":
            target, reply_to = await get_target(e, arg)
            iq = random.randint(50, 160)
            msg = await bot.send_message(
                e.chat_id,
                f"🧠 {target or 'You'} IQ: {iq}",
                reply_to=reply_to
            )
            return await auto_delete(msg, 6)

        # ================= OTHER =================
        if cmd in DATA:
            target, reply_to = await get_target(e, arg)
            choice = random.choice(DATA[cmd])

            if "{target}" in choice:
                choice = choice.format(target=target or "You")

            msg = await bot.send_message(
                e.chat_id,
                f"🎲 {choice}",
                reply_to=reply_to
            )
            return await auto_delete(msg, 6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

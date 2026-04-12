# plugins/fun.py

import random
import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "fun.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "fun",
    ". slap (reply / mention)\n"
    ".hug (reply / mention)\n"
    ".kiss (reply / mention)\n"
    ".poke (reply / mention)\n"
    ".tickle (reply / mention)\n\n"
    "• Fun action commands\n"
    "• Owner only\n"
    "• Auto delete"
)

# =====================
# ACTION DATA
# =====================
ACTIONS = {
    "slap": {
        "gifs": [
            "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
            "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"
        ],
        "texts": [
            "👋 {actor} ne {target} ko zor se thappad mara 😈",
            "💢 {target} ko {actor} se slap pad gaya 😂",
            "🤚 Oops! {actor} ne {target} ko slap kar diya"
        ]
    },
    "hug": {
        "gifs": [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif"
        ],
        "texts": [
            "🤗 {actor} ne {target} ko tight hug diya 💕",
            "🫂 {target} ko {actor} ka hug mila",
            "❤️ {actor} hugged {target}"
        ]
    },
    "kiss": {
        "gifs": [
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif"
        ],
        "texts": [
            "😘 {actor} ne {target} ko kiss diya",
            "💋 {target} got kissed by {actor}",
            "😳 {actor} kissed {target}"
        ]
    },
    "poke": {
        "gifs": [
            "https://media.giphy.com/media/3o6Zt8MgUuvSbkZYWc/giphy.gif",
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
        ],
        "texts": [
            "👉 {actor} ne {target} ko poke kiya 😆",
            "👀 {actor} is poking {target}",
            "😂 {target} ko {actor} ne ched diya"
        ]
    },
    "tickle": {
        "gifs": [
            "https://media.giphy.com/media/11sBLVxNs7v6WA/giphy.gif",
            "https://media.giphy.com/media/l0Exk8EUzSLsrErEQ/giphy.gif"
        ],
        "texts": [
            "🤣 {actor} ne {target} ko gudgudi kar di",
            "😂 {target} control nahi kar pa raha",
            "😹 {actor} ka tickle attack on {target}"
        ]
    }
}

# =====================
# HELPER
# =====================
def mention_user(user):
    name = user.first_name or "User"
    return f"[{name}](tg://user?id={user.id})"

# =====================
# FUN HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"^\.(slap|hug|kiss|poke|tickle)(?:\s|$)"))
async def fun_handler(e):
    if not is_owner(e):
        return

    try:
        cmd = e.pattern_match.group(1)
        data = ACTIONS.get(cmd)
        if not data:
            return

        try:
            await e.delete()
        except:
            pass

        actor = mention_user(await bot.get_entity(e.sender_id))
        target = actor
        reply_to = None

        # =====================
        # REPLY BASED
        # =====================
        if e.is_reply:
            r = await e.get_reply_message()
            if r and r.sender_id:
                user = await bot.get_entity(r.sender_id)
                target = mention_user(user)
                reply_to = r.id

        # =====================
        # MENTION BASED
        # =====================
        elif e.message.entities:
            for ent in e.message.entities:
                if isinstance(ent, MessageEntityMentionName):
                    user = await bot.get_entity(ent.user_id)
                    target = mention_user(user)
                    break

                if isinstance(ent, MessageEntityMention):
                    username = e.raw_text[ent.offset: ent.offset + ent.length]
                    try:
                        user = await bot.get_entity(username)
                        target = mention_user(user)
                        break
                    except:
                        pass

        text = random.choice(data["texts"]).format(
            actor=actor,
            target=target
        )

        if data["gifs"] and random.choice([True, False]):
            msg = await bot.send_file(
                e.chat_id,
                random.choice(data["gifs"]),
                caption=text,
                reply_to=reply_to
            )
        else:
            msg = await bot.send_message(
                e.chat_id,
                text,
                reply_to=reply_to
            )

        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

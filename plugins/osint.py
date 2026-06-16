# plugins/osint.py

import os
import json
import math

from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest

from userbot import bot
from utils.owner import is_owner   # ✅ FIXED
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "osint.py"
DATA_FILE = "utils/osint_store.json"

# =====================
# LOAD / SAVE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"track": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load()

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ osint.py loaded (FIXED)")

# =====================
# HELP
# =====================
register_help(
    "osint",
    ".userinfo (reply / user / id)\n"
    ".numberinfo (reply)\n"
    ".userphotos (reply)\n\n"
    "• Telegram OSINT (ToS-safe)\n"
    "• Owner only\n"
    "• No privacy bypass"
)

# =====================
# UTILS
# =====================
async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    arg = (e.pattern_match.group(1) or "").strip()
    if not arg:
        return None

    if arg.isdigit():
        return int(arg)

    try:
        u = await bot.get_entity(arg)
        return u.id
    except:
        return None

def approx_account_age(uid):
    try:
        year = 2013 + int(math.log10(uid))
        return f"~{year}"
    except:
        return "Unknown"

def risk_score(user, bio):
    score = 0
    if not user.username: score += 15
    if not user.photo: score += 20
    if not bio: score += 10
    if user.bot: score += 40
    if user.scam: score += 50
    if user.fake: score += 30
    if user.verified: score -= 10
    if user.premium: score -= 5
    return max(0, min(score, 100))

# =====================
# USERINFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.userinfo(?:\s+(.+))?$"))
async def userinfo(e):
    if not is_owner(e):
        return  # 🔒 owner only

    try:
        uid = await resolve_user(e)
        if not uid:
            return await e.reply("❌ Reply to a user or give username / id")

        user = await bot.get_entity(uid)
        full = await bot(GetFullUserRequest(uid))

        bio = full.full_user.about or "N/A"
        risk = risk_score(user, bio)

        text = (
            "🧠 **USER OSINT REPORT**\n\n"
            f"• ID: `{user.id}`\n"
            f"• Name: `{(user.first_name or '')} {(user.last_name or '')}`\n"
            f"• Username: `@{user.username or 'N/A'}`\n"
            f"• Bio: `{bio}`\n"
            f"• Phone: `{user.phone or 'Hidden'}`\n"
            f"• Premium: `{bool(user.premium)}`\n"
            f"• Verified: `{bool(user.verified)}`\n"
            f"• Bot: `{bool(user.bot)}`\n"
            f"• Scam: `{bool(user.scam)}`\n"
            f"• Fake: `{bool(user.fake)}`\n"
            f"• Approx Account Age: `{approx_account_age(user.id)}`\n\n"
            f"⚠️ **RISK SCORE:** `{risk}%`\n"
            f"STATUS: `{'HIGH RISK' if risk >= 60 else 'NORMAL'}`"
        )

        await e.reply(text)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# NUMBER INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.numberinfo$"))
async def numberinfo(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        user = await bot.get_entity(uid)

        if not user.phone:
            return await e.reply("❌ Phone number hidden")

        await e.reply(
            f"📞 **NUMBER INFO**\n\n"
            f"• Number: `+{user.phone}`\n"
            f"• Visibility: `Visible to you`"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# USER PHOTOS
# =====================
@bot.on(events.NewMessage(pattern=r"\.userphotos$"))
async def userphotos(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        photos = await bot(GetUserPhotosRequest(uid, 0, 0, 20))
        await e.reply(f"📸 Profile photos: `{len(photos.photos)}`")

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

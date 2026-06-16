# plugins/ban.py

import time
import asyncio
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.plugin_control import is_enabled

PLUGIN_NAME = "ban.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ ban.py loaded")

# =====================
# RIGHTS
# =====================
BAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=False
)

MUTE_BASE_RIGHTS = dict(
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True
)

UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False
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


async def is_admin(chat_id):
    try:
        me = await bot.get_me()
        p = await bot(GetParticipantRequest(chat_id, me.id))
        return bool(p.participant.admin_rights or p.participant.creator)
    except:
        return False


def parse_time(text):
    if not text:
        return None
    try:
        unit = text[-1]
        val = int(text[:-1])
        if unit == "m":
            return val * 60
        if unit == "h":
            return val * 3600
        if unit == "d":
            return val * 86400
    except:
        return None


async def ensure_participant(chat_id, uid):
    try:
        await bot(GetParticipantRequest(chat_id, uid))
        return True
    except:
        return False

# =====================
# HELP
# =====================
register_help(
    "ban",
    ".ban <reply/user/id> [reason]\n"
    ".unban <reply/user/id> [reason]\n"
    ".mute [time] [reason]\n"
    ".unmute [reason]\n\n"
    "• ONLY userbot owner can use\n"
    "• Userbot must be admin\n"
    "• Time: 10m / 2h / 1d"
)

# =====================
# BAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ban(?: (.*))?$"))
async def ban_user(e):
    if not e.is_group or not is_owner(e):
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid or not await ensure_participant(e.chat_id, uid):
            return

        reason = e.pattern_match.group(1) or "No reason"

        await bot(EditBannedRequest(e.chat_id, uid, BAN_RIGHTS))
        await e.delete()

        msg = await bot.send_message(
            e.chat_id,
            f"🚫 **USER BANNED**\nUser: `{uid}`\nReason: `{reason}`"
        )
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# UNBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.unban(?: (.*))?$"))
async def unban_user(e):
    if not e.is_group or not is_owner(e):
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        await bot(EditBannedRequest(e.chat_id, uid, UNBAN_RIGHTS))
        await e.delete()

        msg = await bot.send_message(
            e.chat_id,
            f"✅ **USER UNBANNED**\nUser: `{uid}`\nNote: `{reason}`"
        )
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# MUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.mute(?: (.*))?$"))
async def mute_user(e):
    if not e.is_group or not is_owner(e):
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid or not await ensure_participant(e.chat_id, uid):
            return

        args = (e.pattern_match.group(1) or "").split()
        duration = parse_time(args[0]) if args else None
        reason = " ".join(args[1:]) if duration else " ".join(args)
        reason = reason or "No reason"

        until = int(time.time()) + duration if duration else None

        rights = ChatBannedRights(
            until_date=until,
            **MUTE_BASE_RIGHTS
        )

        await bot(EditBannedRequest(e.chat_id, uid, rights))
        await e.delete()

        msg = await bot.send_message(
            e.chat_id,
            f"🔇 **USER MUTED**\n"
            f"User: `{uid}`\n"
            f"Duration: `{args[0] if duration else 'Permanent'}`\n"
            f"Reason: `{reason}`"
        )

        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# UNMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.unmute(?: (.*))?$"))
async def unmute_user(e):
    if not e.is_group or not is_owner(e):
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        await bot(EditBannedRequest(e.chat_id, uid, UNMUTE_RIGHTS))
        await e.delete()

        msg = await bot.send_message(
            e.chat_id,
            f"🔊 **USER UNMUTED**\nUser: `{uid}`\nNote: `{reason}`"
        )

        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

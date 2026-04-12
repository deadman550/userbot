# plugins/moderation.py

import time
import json
import os
import asyncio
from datetime import datetime

from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "moderation.py"
DATA_FILE = "utils/moderation_data.json"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ moderation.py loaded (STABLE + ADMIN AWARE)")

# =====================
# STORAGE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"gbans": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load()

# =====================
# UTILS
# =====================
def now():
    return int(time.time())

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

# =====================
# RIGHTS (TELETHON SAFE)
# =====================
BAN = ChatBannedRights(
    until_date=None,
    view_messages=True
)

UNBAN = ChatBannedRights(
    until_date=None,
    view_messages=False
)

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".gban <reply/user/id> [reason]\n"
    ".ungban <user>\n"
    ".gbaninfo <user>\n"
    ".gbanlist\n\n"
    ".kick <reply/user/id> [reason]\n\n"
    "• Admin-aware global ban\n"
    "• Skips non-admin groups\n"
    "• Kick = ban + unban (current group)\n"
    "• Fully Telethon compatible"
)

# =====================
# GBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?: (.*))?$"))
async def gban(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        DATA["gbans"][str(uid)] = {
            "time": now(),
            "reason": reason
        }
        save()

        affected = 0

        async for d in bot.iter_dialogs():
            if not (d.is_group or d.is_channel):
                continue
            if not await is_admin(d.id):
                continue
            try:
                await bot(EditBannedRequest(d.id, uid, BAN))
                affected += 1
            except:
                pass

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"🚫 **GLOBAL BAN APPLIED**\n"
            f"User: `{uid}`\n"
            f"Reason: `{reason}`\n"
            f"Affected chats: `{affected}`"
        )
        await asyncio.sleep(8)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# UNGBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungban(?: (.*))?$"))
async def ungban(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        DATA["gbans"].pop(str(uid), None)
        save()

        async for d in bot.iter_dialogs():
            if not (d.is_group or d.is_channel):
                continue
            if not await is_admin(d.id):
                continue
            try:
                await bot(EditBannedRequest(d.id, uid, UNBAN))
            except:
                pass

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"✅ **GLOBAL BAN REMOVED**\nUser: `{uid}`"
        )
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# KICK (CURRENT GROUP)
# =====================
@bot.on(events.NewMessage(pattern=r"\.kick(?: (.*))?$"))
async def kick_user(e):
    if not e.is_group:
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        # ban
        await bot(EditBannedRequest(e.chat_id, uid, BAN))
        await asyncio.sleep(1)
        # unban = kick
        await bot(EditBannedRequest(e.chat_id, uid, UNBAN))

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"👢 **USER KICKED**\nUser: `{uid}`\nReason: `{reason}`"
        )
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# GBAN INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.gbaninfo(?: (.*))?$"))
async def gbaninfo(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    data = DATA["gbans"].get(str(uid))

    await e.delete()

    if not data:
        msg = await bot.send_message(
            e.chat_id,
            f"ℹ️ User `{uid}` is not globally banned"
        )
        await asyncio.sleep(6)
        await msg.delete()
        return

    msg = await bot.send_message(
        e.chat_id,
        f"🚫 **GBAN INFO**\n"
        f"User: `{uid}`\n"
        f"Time: `{datetime.fromtimestamp(data['time'])}`\n"
        f"Reason: `{data.get('reason')}`"
    )
    await asyncio.sleep(10)
    await msg.delete()

# =====================
# GBAN LIST
# =====================
@bot.on(events.NewMessage(pattern=r"\.gbanlist$"))
async def gbanlist(e):
    if not is_owner(e):
        return

    text = "🚫 **GLOBAL BANS**\n\n"
    for uid, d in DATA["gbans"].items():
        text += f"• `{uid}` → {d.get('reason')}\n"

    await e.reply(text or "No global bans")

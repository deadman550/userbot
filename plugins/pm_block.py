# plugins/pm_block.py

import asyncio
from telethon import events
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "pm_block.py"

mark_plugin_loaded(PLUGIN_NAME)
print("✔ pm_block.py loaded")

# =====================
# HELP
# =====================
register_help(
    "pm_block",
    ".block (reply / user / id)\n"
    ".unblock (reply / user / id)\n\n"
    "• Private DM level block\n"
    "• Does NOT affect groups"
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

    try:
        if arg.isdigit():
            return int(arg)
        u = await bot.get_entity(arg)
        return u.id
    except:
        return None

# =====================
# BLOCK
# =====================
@bot.on(events.NewMessage(pattern=r"\.block(?:\s+(.+))?$"))
async def block_user(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        await e.delete()
        await bot(BlockRequest(uid))

        m = await bot.send_message(e.chat_id, "🚫 User blocked (PM)")
        await asyncio.sleep(5)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# UNBLOCK
# =====================
@bot.on(events.NewMessage(pattern=r"\.unblock(?:\s+(.+))?$"))
async def unblock_user(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        await e.delete()
        await bot(UnblockRequest(uid))

        m = await bot.send_message(e.chat_id, "✅ User unblocked (PM)")
        await asyncio.sleep(5)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

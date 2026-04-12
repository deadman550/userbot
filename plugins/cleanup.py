import asyncio
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "cleanup.py"

# =====================
# PLUGIN LOAD (health)
# =====================
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "cleanup",
    ".purge (reply)\n"
    "Delete messages between replied msg and command\n\n"
    ".clean COUNT\n"
    "Delete last messages (admin = all, user = own)\n\n"
    ".del (reply)\n"
    "Delete single message\n\n"
    ".delall (reply to user)\n"
    "Delete all messages of a user\n\n"
    "• Admin = full power\n"
    "• User = only own messages\n"
    "• Flood safe batch delete"
)

# =====================
# HELPER: CHECK ADMIN
# =====================
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        p = await bot(GetParticipantRequest(chat_id, user_id))
        return isinstance(
            p.participant,
            (ChannelParticipantAdmin, ChannelParticipantCreator)
        )
    except Exception:
        return False


# =====================
# PURGE
# =====================
@bot.on(events.NewMessage(pattern=r"\.purge$"))
async def purge_handler(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        reply = await e.get_reply_message()

        # 🔥 SAFETY FIX (TotalList / None)
        if isinstance(reply, list):
            reply = reply[0] if reply else None
        if not reply:
            return

        await e.delete()

        chat_id = e.chat_id
        user_id = e.sender_id

        start_id = reply.id
        end_id = e.id - 1

        if start_id > end_id:
            return

        admin = await is_admin(chat_id, user_id)
        msg_ids = []

        async for msg in bot.iter_messages(
            chat_id,
            min_id=start_id - 1,
            max_id=end_id
        ):
            if admin or msg.sender_id == user_id:
                msg_ids.append(msg.id)

        for i in range(0, len(msg_ids), 100):
            await bot.delete_messages(chat_id, msg_ids[i:i + 100])
            await asyncio.sleep(0.5)

        done = await bot.send_message(chat_id, "✅ Purge complete")
        await asyncio.sleep(3)
        await done.delete()

    except Exception as err:
        mark_plugin_error(PLUGIN_NAME, err)
        await log_error(bot, PLUGIN_NAME, err)

# =====================
# CLEAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.clean (\d+)"))
async def clean_handler(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        count = int(e.pattern_match.group(1))
        chat_id = e.chat_id
        user_id = e.sender_id

        admin = await is_admin(chat_id, user_id)
        msg_ids = []

        async for msg in bot.iter_messages(chat_id, limit=count):
            if admin or msg.sender_id == user_id:
                msg_ids.append(msg.id)

        for i in range(0, len(msg_ids), 100):
            await bot.delete_messages(chat_id, msg_ids[i:i + 100])
            await asyncio.sleep(0.5)

        done = await bot.send_message(
            chat_id,
            f"✅ Cleaned {len(msg_ids)} messages"
        )
        await asyncio.sleep(3)
        await done.delete()

    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(bot, PLUGIN_NAME, e)


# =====================
# DEL
# =====================
@bot.on(events.NewMessage(pattern=r"\.del$"))
async def del_single(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        target = await e.get_reply_message()
        chat_id = e.chat_id
        user_id = e.sender_id

        admin = await is_admin(chat_id, user_id)
        if not admin and target.sender_id != user_id:
            return

        await bot.delete_messages(chat_id, target.id)

    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(bot, PLUGIN_NAME, e)


# =====================
# DELALL
# =====================
@bot.on(events.NewMessage(pattern=r"\.delall$"))
async def del_all(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        target = await e.get_reply_message()
        chat_id = e.chat_id
        user_id = e.sender_id

        admin = await is_admin(chat_id, user_id)
        if not admin and target.sender_id != user_id:
            return

        msg_ids = []

        async for msg in bot.iter_messages(chat_id, limit=1000):
            if msg.sender_id == target.sender_id:
                msg_ids.append(msg.id)

        for i in range(0, len(msg_ids), 100):
            await bot.delete_messages(chat_id, msg_ids[i:i + 100])
            await asyncio.sleep(0.5)

        done = await bot.send_message(
            chat_id,
            f"✅ Deleted {len(msg_ids)} messages"
        )
        await asyncio.sleep(3)
        await done.delete()

    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(bot, PLUGIN_NAME, e)

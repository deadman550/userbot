import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("forward.py")
print("✔ forward.py loaded")


# =====================
# TARGET PARSER
# =====================
def parse_target(raw: str):
    raw = raw.strip()
    if raw.lstrip("-").isdigit():
        return int(raw)
    return raw


# =====================
# FWD
# =====================
@bot.on(events.NewMessage(pattern=r"\.fwd(?:\s+(.*))?$"))
async def fwd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        raw = e.pattern_match.group(1)
        if not raw:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.fwd CHAT_ID or @username"
            )
            await asyncio.sleep(4)
            await msg.delete()
            return

        target = parse_target(raw)
        reply = await e.get_reply_message()

        await bot.forward_messages(target, reply)

        done = await bot.send_message(e.chat_id, "✅ Forwarded")
        await asyncio.sleep(3)
        await done.delete()

    except Exception as ex:
        mark_plugin_error("forward.py", ex)
        await log_error(bot, "forward.py", ex)


# =====================
# SILENT FWD
# =====================
@bot.on(events.NewMessage(pattern=r"\.sfwd(?:\s+(.*))?$"))
async def silent_fwd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        raw = e.pattern_match.group(1)
        if not raw:
            return

        target = parse_target(raw)
        reply = await e.get_reply_message()

        await bot.forward_messages(target, reply)

    except Exception as ex:
        mark_plugin_error("forward.py", ex)
        await log_error(bot, "forward.py", ex)


# =====================
# FWD HERE
# =====================
@bot.on(events.NewMessage(pattern=r"\.fwdhere$"))
async def fwd_here(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        reply = await e.get_reply_message()
        await bot.forward_messages(e.chat_id, reply)

        done = await bot.send_message(e.chat_id, "✅ Forwarded here")
        await asyncio.sleep(3)
        await done.delete()

    except Exception as ex:
        mark_plugin_error("forward.py", ex)
        await log_error(bot, "forward.py", ex)


# =====================
# MULTI FWD
# =====================
@bot.on(events.NewMessage(pattern=r"\.mfwd(?:\s+(.*))?$"))
async def multi_fwd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        args = (e.pattern_match.group(1) or "").split()
        if len(args) < 2 or not args[1].isdigit():
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.mfwd CHAT_ID or @username COUNT"
            )
            await asyncio.sleep(4)
            await msg.delete()
            return

        target = parse_target(args[0])
        count = int(args[1])

        reply = await e.get_reply_message()
        start_id = reply.id
        success = 0

        for msg_id in range(start_id, start_id + count):
            try:
                await bot.forward_messages(
                    target,
                    e.chat_id,
                    msg_id
                )
                success += 1
                await asyncio.sleep(0.4)
            except Exception:
                pass

        done = await bot.send_message(
            e.chat_id,
            f"✅ Forwarded {success} messages"
        )
        await asyncio.sleep(3)
        await done.delete()

    except Exception as ex:
        mark_plugin_error("forward.py", ex)
        await log_error(bot, "forward.py", ex)

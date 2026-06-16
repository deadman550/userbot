# plugins/stats.py

import time
import asyncio
from telethon import events
from telethon.tl.types import Channel, Chat

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "stats.py"

print("✔ stats.py loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "info",
    ".stats\n\n"
    "Shows profile statistics\n"
    "• Groups / Channels count\n"
    "• Admin & Owner info\n"
    "• Session message count\n"
    "• Bot uptime"
)

# =====================
# GLOBAL STATS
# =====================
START_TIME = time.time()
MSG_COUNT = 0


def uptime():
    s = int(time.time() - START_TIME)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}h {m}m {s}s"


# =====================
# MESSAGE COUNTER
# =====================
@bot.on(events.NewMessage(outgoing=True))
async def count_my_messages(e):
    global MSG_COUNT
    if is_owner(e):
        MSG_COUNT += 1


# =====================
# STATS COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.stats$"))
async def stats_handler(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        # 🔹 Step-1: Initial message
        msg = await bot.send_message(e.chat_id, "📊 Collecting stats")

        # 🔹 Step-2: Small SAFE animation (not infinite)
        for dots in [".", "..", "..."]:
            await asyncio.sleep(0.7)
            await msg.edit(f"📊 Collecting stats{dots}")

        me = await bot.get_me()

        groups = channels = 0
        g_admin = g_owner = 0
        c_admin = c_owner = 0

        # 🔹 Step-3: Heavy work
        async for dialog in bot.iter_dialogs(limit=1500):
            entity = dialog.entity

            try:
                if isinstance(entity, Chat):
                    groups += 1
                    p = await bot.get_permissions(entity, me)
                    if p.is_creator:
                        g_owner += 1
                    elif p.is_admin:
                        g_admin += 1

                elif isinstance(entity, Channel):
                    if entity.megagroup:
                        groups += 1
                        p = await bot.get_permissions(entity, me)
                        if p.is_creator:
                            g_owner += 1
                        elif p.is_admin:
                            g_admin += 1
                    else:
                        channels += 1
                        p = await bot.get_permissions(entity, me)
                        if p.is_creator:
                            c_owner += 1
                        elif p.is_admin:
                            c_admin += 1
            except:
                continue

        # 🔹 Step-4: Final result
        text = (
            "📊 **Telegram Profile Stats**\n\n"
            f"👤 User: {me.first_name}\n"
            f"🆔 Your ID: `{me.id}`\n\n"
            f"👥 Groups: `{groups}`\n"
            f"🛡 Admin in Groups: `{g_admin}`\n"
            f"👑 Owner of Groups: `{g_owner}`\n\n"
            f"📢 Channels: `{channels}`\n"
            f"🛡 Admin in Channels: `{c_admin}`\n"
            f"👑 Owner of Channels: `{c_owner}`\n\n"
            f"💬 Messages Sent (session): `{MSG_COUNT}`\n"
            f"⏱ Uptime: `{uptime()}`"
        )

        await msg.edit(text)
        await asyncio.sleep(20)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# plugins/antipm.py

import time
import asyncio
from datetime import datetime

from telethon import events
from telethon.tl.functions.contacts import BlockRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

from utils.local_store import (
    get_state,
    set_state,
    get_user,
    save_user,
    reset_user,
    list_users
)

PLUGIN_NAME = "antipm.py"

mark_plugin_loaded(PLUGIN_NAME)
print("✔ antipm.py loaded (local_store + mute mode)")

# =====================
# CONFIG
# =====================
WARNING_LIMIT = 3
SPAM_LIMIT = 5
SPAM_WINDOW = 10   # seconds


# =====================
# UTILS
# =====================
def ts(t):
    if not t:
        return "N/A"
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def parse_time(arg):
    if arg.endswith("m"):
        return int(arg[:-1]) * 60
    if arg.endswith("h"):
        return int(arg[:-1]) * 3600
    if arg.endswith("d"):
        return int(arg[:-1]) * 86400
    return None


async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    arg = e.pattern_match.group(1)
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
# HELP
# =====================
register_help(
    "antipm",
    ".antipm on | off\n"
    ".antipms on | off\n"
    ".antipmmute <10m|1h|1d|off>\n"
    ".antipmstatus\n"
    ".antipmlist\n"
    ".approve (reply / user / id)\n"
    ".disapprove (reply / user / id)\n"
    ".resetwarn (reply / user / id)\n\n"
    "• Local disk based\n"
    "• Block / Mute mode\n"
    "• Warning replace system\n"
    "• DM only"
)


# =====================
# TOGGLES
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm (on|off)$"))
async def toggle_antipm(e):
    if not is_owner(e):
        return

    val = e.pattern_match.group(1) == "on"
    set_state("enabled", val)

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if val else 'DISABLED'}"
    )
    await asyncio.sleep(5)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.antipms (on|off)$"))
async def toggle_silent(e):
    if not is_owner(e):
        return

    set_state("enabled", True)
    set_state("silent", e.pattern_match.group(1) == "on")

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🔇 Silent mode {'ON' if get_state().get('silent') else 'OFF'}"
    )
    await asyncio.sleep(5)
    await m.delete()


# =====================
# MUTE MODE
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmmute(?:\s+(\S+))?$"))
async def antipm_mute(e):
    if not is_owner(e):
        return

    arg = e.pattern_match.group(1)

    if not arg or arg == "off":
        set_state("mode", "block")
        set_state("mute_time", None)
        await e.delete()
        return await bot.send_message(e.chat_id, "🔓 Mute mode disabled")

    sec = parse_time(arg)
    if not sec:
        return await bot.send_message(
            e.chat_id,
            "❌ Invalid time\nUse: 10m / 1h / 1d"
        )

    set_state("enabled", True)
    set_state("mode", "mute")
    set_state("mute_time", sec)

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🔕 Anti-PM MUTE enabled for `{arg}`"
    )
    await asyncio.sleep(5)
    await m.delete()


# =====================
# STATUS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmstatus$"))
async def antipm_status(e):
    if not is_owner(e):
        return

    s = get_state()
    users = list_users()

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        "🛡 **Anti-PM Status**\n\n"
        f"• Enabled: `{s.get('enabled', True)}`\n"
        f"• Silent: `{s.get('silent', False)}`\n"
        f"• Mode: `{s.get('mode','block')}`\n"
        f"• Mute time: `{s.get('mute_time') or 'N/A'}`\n"
        f"• Tracked users: `{len(users)}`\n"
        f"• Last blocked: `{s.get('last_blocked_user') or 'N/A'}`\n"
        f"• Last warning: `{ts(s.get('last_warning_time'))}`"
    )
    await asyncio.sleep(12)
    await m.delete()


# =====================
# LIST USERS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmlist$"))
async def antipm_list(e):
    if not is_owner(e):
        return

    users = list_users()
    await e.delete()

    if not users:
        m = await bot.send_message(e.chat_id, "📭 No tracked users")
        await asyncio.sleep(5)
        return await m.delete()

    text = "🛡 **Anti-PM Users**\n\n"
    for uid, u in users.items():
        text += (
            f"• `{uid}` | "
            f"warn: `{u.get('warnings',0)}` | "
            f"approved: `{u.get('approved',False)}` | "
            f"muted till: `{ts(u.get('muted_until'))}`\n"
        )

    m = await bot.send_message(e.chat_id, text)
    await asyncio.sleep(15)
    await m.delete()


# =====================
# APPROVE / DISAPPROVE / RESET
# =====================
@bot.on(events.NewMessage(pattern=r"\.approve(?:\s+(.+))?$"))
async def approve_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    save_user(uid, {
        "approved": True,
        "warnings": 0,
        "msgs": [],
        "muted_until": None
    })

    await e.delete()
    await bot.send_message(e.chat_id, "✅ User approved")


@bot.on(events.NewMessage(pattern=r"\.disapprove(?:\s+(.+))?$"))
async def disapprove_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if uid:
        reset_user(uid)

    await e.delete()
    await bot.send_message(e.chat_id, "❌ User disapproved")


@bot.on(events.NewMessage(pattern=r"\.resetwarn(?:\s+(.+))?$"))
async def resetwarn(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    save_user(uid, {
        "approved": False,
        "warnings": 0,
        "msgs": [],
        "muted_until": None
    })

    await e.delete()
    await bot.send_message(e.chat_id, "🔄 Warnings reset")


# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or is_owner(e):
        return

    s = get_state()
    if not s.get("enabled", True):
        return

    try:
        sender = await e.get_sender()
        uid = sender.id

        if sender.bot or sender.verified:
            return

        u = get_user(uid)
        now = time.time()

        # muted user → ignore
        if u and u.get("muted_until") and now < u["muted_until"]:
            return

        if u and u.get("approved"):
            return

        if not u:
            save_user(uid, {
                "approved": False,
                "warnings": 0,
                "msgs": [now],
                "muted_until": None
            })

            if not s.get("silent"):
                await bot.send_message(
                    uid,
                    "👋 Hello!\n\nThis account doesn’t accept DMs.\n"
                    "Please wait for approval."
                )
            return

        msgs = [t for t in u.get("msgs", []) if now - t < SPAM_WINDOW] + [now]

        warnings = u.get("warnings", 0) + 1
        set_state("last_warning_time", now)

        if warnings >= WARNING_LIMIT:
            if s.get("mode") == "mute":
                u["muted_until"] = now + s.get("mute_time", 3600)
                save_user(uid, u)

                if not s.get("silent"):
                    await bot.send_message(
                        uid,
                        "🔕 You are temporarily muted due to repeated messages."
                    )
                return
            else:
                set_state("last_blocked_user", uid)
                if not s.get("silent"):
                    await bot.send_message(
                        uid,
                        "🚫 You have been blocked due to repeated warnings."
                    )
                await asyncio.sleep(1)
                await bot(BlockRequest(uid))
                reset_user(uid)
                return

        save_user(uid, {
            "approved": False,
            "warnings": warnings,
            "msgs": msgs,
            "muted_until": None
        })

        if not s.get("silent"):
            await bot.send_message(
                uid,
                f"⚠️ Warning {warnings}/{WARNING_LIMIT}\n"
                "Please stop messaging without approval."
            )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

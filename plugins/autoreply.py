# plugins/autoreply.py

import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.mongo import settings

PLUGIN_NAME = "autoreply.py"
print("✔ autoreply.py loaded (SMART v2 – FINAL PATCHED)")

# =====================
# HELP
# =====================
register_help(
    "autoreply",
    ".autoreply on|off\n"
    ".autoreply status\n"
    ".autoreplydelay <sec>\n"
    ".autocooldown <sec>\n\n"
    ".seenonly on|off\n"
    ".firstreply on|off\n"
    ".setfirstreply TEXT\n"
    ".autodisable on|off\n\n"
    ".officehours on|off\n"
    ".officehours set <start>-<end>\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    ".awhitelist (reply/user/id)\n"
    ".awhitelistdel (reply/user/id)\n"
    ".awhitelist list\n\n"
    ".ablacklist (reply/user/id)\n"
    ".ablacklistdel (reply/user/id)\n"
    ".ablacklist list\n\n"
    "• DM only\n"
    "• Mongo based\n"
    "• Smart v2 (stable)"
)

# =====================
# RUNTIME MEMORY
# =====================
LAST_REPLY_TIME = {}     # uid -> datetime
LAST_AUTOREPLY = {}     # uid -> Message
DISABLED_USERS = set()

# =====================
# DEFAULT TEXTS
# =====================
TIME_TEXTS = {
    "morning": "☀️ Good morning!\nI will reply soon 😊",
    "afternoon": "🌤 Hello!\nI am busy right now.",
    "evening": "🌆 Good evening!\nWill get back to you soon.",
    "night": "🌙 It's late night.\nPlease text, I’ll reply later 🙏"
}

DEFAULT_FIRST_REPLY = "👋 Hi! Thanks for messaging.\nI’ll reply shortly."

# =====================
# DB HELPERS
# =====================
def get_var(k, d=None):
    doc = settings.find_one({"_id": k})
    return doc["value"] if doc else d

def set_var(k, v):
    settings.update_one(
        {"_id": k},
        {"$set": {"value": v}},
        upsert=True
    )

def get_list(k):
    raw = get_var(k, "")
    if not raw:
        return []
    return [int(x) for x in raw.split(",") if x.isdigit()]

def save_list(k, data):
    set_var(k, ",".join(str(x) for x in data))

# =====================
# UTILS
# =====================
async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id if r else None

    parts = e.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        return None

    arg = parts[1].strip()

    if arg.isdigit():
        return int(arg)

    try:
        u = await bot.get_entity(arg)
        return u.id
    except:
        return None

# =====================
# FLAGS
# =====================
def enabled(): return get_var("AUTOREPLY_ON", "off") == "on"
def cooldown(): return int(get_var("AR_COOLDOWN", "0"))
def seen_only(): return get_var("AR_SEENONLY", "off") == "on"
def firstreply(): return get_var("AR_FIRST", "off") == "on"
def autodisable(): return get_var("AR_AUTODISABLE", "off") == "on"

# =====================
# OFFICE HOURS
# =====================
def outside_office_hours():
    if get_var("AR_OFFICE", "off") != "on":
        return False
    t = get_var("AR_OFFICE_TIME")
    if not t:
        return False
    s, e = map(int, t.split("-"))
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    return not (s <= h <= e)

# =====================
# TEXT HELPERS
# =====================
def time_text():
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    if 5 <= h <= 11:
        return get_var("AUTOREPLY_MORNING", TIME_TEXTS["morning"])
    if 12 <= h <= 16:
        return get_var("AUTOREPLY_AFTERNOON", TIME_TEXTS["afternoon"])
    if 17 <= h <= 20:
        return get_var("AUTOREPLY_EVENING", TIME_TEXTS["evening"])
    return get_var("AUTOREPLY_NIGHT", TIME_TEXTS["night"])

def first_reply_text():
    return get_var("AR_FIRST_TEXT", DEFAULT_FIRST_REPLY)

# =====================
# OWNER COMMANDS (PATCHED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.autoreply (on|off)"))
async def _(e):
    if not is_owner(e):
        return
    state = e.pattern_match.group(1)
    set_var("AUTOREPLY_ON", state)
    await e.delete()
    m = await e.respond(
        f"Autoreply {'Enabled' if state=='on' else 'Disabled'} ✅"
    )
    await asyncio.sleep(3)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.autoreply status$"))
async def _(e):
    if not is_owner(e):
        return
    await e.delete()
    m = await e.respond(
        "📊 **AUTOREPLY STATUS**\n\n"
        f"• Status: `{ 'ON' if enabled() else 'OFF' }`\n"
        f"• Delay: `{ get_var('AUTOREPLY_DELAY','0') } sec`\n"
        f"• Cooldown: `{ cooldown() } sec`\n"
        f"• Seen only: `{ get_var('AR_SEENONLY','off').upper() }`\n"
        f"• First reply: `{ get_var('AR_FIRST','off').upper() }`\n\n"
        f"• Whitelist: `{ len(get_list('AUTOREPLY_WHITELIST')) }`\n"
        f"• Blacklist: `{ len(get_list('AUTOREPLY_BLACKLIST')) }`"
    )
    await asyncio.sleep(4)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def _(e):
    if not is_owner(e):
        return
    set_var("AUTOREPLY_DELAY", e.pattern_match.group(1))
    await e.delete()
    m = await e.respond("Delay updated ⏱")
    await asyncio.sleep(3)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.autocooldown (\d+)"))
async def _(e):
    if not is_owner(e):
        return
    set_var("AR_COOLDOWN", e.pattern_match.group(1))
    await e.delete()
    m = await e.respond("Cooldown updated ⏳")
    await asyncio.sleep(3)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.(firstreply|seenonly|autodisable) (on|off)"))
async def _(e):
    if not is_owner(e):
        return
    keymap = {
        "firstreply": "AR_FIRST",
        "seenonly": "AR_SEENONLY",
        "autodisable": "AR_AUTODISABLE",
    }
    set_var(keymap[e.pattern_match.group(1)], e.pattern_match.group(2))
    await e.delete()
    m = await e.respond("Setting updated ✅")
    await asyncio.sleep(3)
    await m.delete()


# =====================
# SET TEXT (MULTILINE SAFE + CONFIRM)
# =====================
@bot.on(events.NewMessage(pattern=r"\.setf(irst)?reply"))
async def _(e):
    if not is_owner(e):
        return
    text = e.raw_text.split(None, 1)[1]
    set_var("AR_FIRST_TEXT", text)
    await e.delete()
    m = await e.respond("First reply text updated ✨")
    await asyncio.sleep(3)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.set(morning|afternoon|evening|night)"))
async def _(e):
    if not is_owner(e):
        return
    text = e.raw_text.split(None, 1)[1]
    set_var(f"AUTOREPLY_{e.pattern_match.group(1).upper()}", text)
    await e.delete()
    m = await e.respond(f"{e.pattern_match.group(1).title()} reply updated ✅")
    await asyncio.sleep(3)
    await m.delete()


# =====================
# WHITELIST / BLACKLIST (PATCHED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.a(white|black)list\s+(.+)$"))
async def _(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    if not uid:
        await e.delete()
        m = await e.respond("❌ User not found")
        await asyncio.sleep(3)
        await m.delete()
        return

    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    data = get_list(key)

    if uid not in data:
        data.append(uid)
        save_list(key, data)

    await e.delete()
    m = await e.respond("User added ✅")
    await asyncio.sleep(3)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.a(white|black)listdel(?: .+)?$"))
async def _(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    if not uid:
        await e.delete()
        m = await e.respond("❌ User not found")
        await asyncio.sleep(3)
        await m.delete()
        return

    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    data = get_list(key)

    if uid in data:
        data.remove(uid)
        save_list(key, data)

    await e.delete()
    m = await e.respond("User removed 🗑")
    await asyncio.sleep(3)
    await m.delete()

@bot.on(events.NewMessage(pattern=r"\.a(white|black)list list$"))
async def list_users(e):
    if not is_owner(e):
        return

    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    users = get_list(key)

    await e.delete()

    if not users:
        m = await e.respond("📭 List empty")
        await asyncio.sleep(3)
        await m.delete()
        return

    text = "📃 **USER LIST**\n\n"
    for uid in users:
        try:
            u = await bot.get_entity(uid)
            uname = f"@{u.username}" if u.username else ""
            text += f"• {u.first_name or 'User'} {uname} (`{uid}`)\n"
        except:
            text += f"• `{uid}`\n"

    m = await e.respond(text)
    await asyncio.sleep(5)
    await m.delete()
# =====================
# AUTOREPLY CORE (BOT FILTER FIXED)
# =====================
@bot.on(events.NewMessage(incoming=True))
async def autoreply(e):
    try:
        if not e.is_private or is_owner(e):
            return

        sender = await e.get_sender()
        if not sender or sender.bot:
            return  # 🚫 bots ignored

        uid = sender.id

        if not enabled():
            return

        if uid in get_list("AUTOREPLY_BLACKLIST"):
            return

        wl = get_list("AUTOREPLY_WHITELIST")
        if wl and uid not in wl:
            return

        if seen_only():
            await bot.send_read_acknowledge(e.chat_id)
            return

        now = datetime.utcnow()
        if uid in LAST_REPLY_TIME and (now - LAST_REPLY_TIME[uid]).seconds < cooldown():
            return

        old = LAST_AUTOREPLY.get(uid)
        if old:
            try:
                await old.delete()
            except:
                pass

        text = (
            first_reply_text()
            if firstreply() and uid not in LAST_REPLY_TIME
            else time_text()
        )

        msg = await e.reply(text)
        LAST_AUTOREPLY[uid] = msg
        LAST_REPLY_TIME[uid] = now

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

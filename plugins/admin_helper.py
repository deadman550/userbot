# plugins/admin_helper.py

import asyncio
from telethon import events
from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.mongo import settings

PLUGIN_NAME = "admin_helper.py"
print("✔ admin_helper.py loaded (ADMIN HELPER)")

WARN_LIMIT = 3

# =====================
# HELP
# =====================
register_help(
    "admin",
    ".admins\n"
    ".setrules text\n"
    ".rules\n"
    ".warn @user reason\n"
    ".warns @user\n"
    ".clearwarn @user\n\n"
    "• Admin helper\n"
    "• Warn limit 3"
)

# =====================
# DB HELPERS
# =====================
def get_warn(uid):
    d = settings.find_one({"_id": f"warn_{uid}"})
    return d["count"] if d else 0

def set_warn(uid, c):
    settings.update_one(
        {"_id": f"warn_{uid}"},
        {"$set": {"count": c}},
        upsert=True
    )

# =====================
# ADMINS
# =====================
@bot.on(events.NewMessage(pattern=r"\.admins$"))
async def admins(e):
    if not e.is_group:
        return
    admins = await bot.get_participants(e.chat_id, filter=events.ChatParticipantsAdmins)
    text = "👮 **Admins**\n\n"
    for a in admins:
        text += f"• {a.first_name}\n"
    await e.edit(text)

# =====================
# RULES
# =====================
@bot.on(events.NewMessage(pattern=r"\.setrules\s+(.+)"))
async def set_rules(e):
    settings.update_one(
        {"_id": f"rules_{e.chat_id}"},
        {"$set": {"text": e.pattern_match.group(1)}},
        upsert=True
    )
    await e.edit("✅ Rules updated")

@bot.on(events.NewMessage(pattern=r"\.rules$"))
async def rules(e):
    d = settings.find_one({"_id": f"rules_{e.chat_id}"})
    if not d:
        return await e.edit("❌ No rules set")
    await e.edit(f"📜 **Rules**\n\n{d['text']}")

# =====================
# WARN SYSTEM
# =====================
@bot.on(events.NewMessage(pattern=r"\.warn(?:\s+(.*))?$"))
async def warn(e):
    if not e.is_reply:
        return await e.edit("Reply to user")
    r = await e.get_reply_message()
    uid = r.sender_id

    c = get_warn(uid) + 1
    set_warn(uid, c)

    await e.edit(
        f"⚠️ **Warning issued**\n\n"
        f"User: `{uid}`\n"
        f"Reason: {e.pattern_match.group(1) or 'Rule break'}\n"
        f"Warns: {c}/{WARN_LIMIT}"
    )

@bot.on(events.NewMessage(pattern=r"\.warns$"))
async def warns(e):
    if not e.is_reply:
        return
    r = await e.get_reply_message()
    await e.edit(f"⚠️ Warns: {get_warn(r.sender_id)}/{WARN_LIMIT}")

@bot.on(events.NewMessage(pattern=r"\.clearwarn$"))
async def clearwarn(e):
    if not e.is_reply:
        return
    r = await e.get_reply_message()
    set_warn(r.sender_id, 0)
    await e.edit("✅ Warns cleared")

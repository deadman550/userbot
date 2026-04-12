import os
import time
import asyncio
from datetime import datetime

from telethon import events
from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.mongo import mongo

PLUGIN_NAME = "profilecopy.py"
print(f"✔ {PLUGIN_NAME} loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# GLOBAL STATE
# =====================
CLONE_TASK = None
CLONE_END_TIME = 0
SILENT_CLONE = False

# =====================
# HELP
# =====================
register_help(
    "profilecopy",
    ".copyname (reply)\n"
    ".copybio (reply)\n"
    ".copydp (reply)\n\n"
    ".clone SECONDS (reply)\n"
    ".silentclone on | off\n\n"
    ".backupprofile\n"
    ".backupprofile force\n"
    ".restoreprofile\n"
    ".backupinfo"
)

# =====================
# MONGO
# =====================
db = mongo["userbot"]
profile_col = db["profile_backup"]

# =====================
# INTERNAL HELPERS
# =====================
async def set_name(user):
    await bot(functions.account.UpdateProfileRequest(
        first_name=user.first_name,
        last_name=user.last_name
    ))

async def set_bio(user):
    full = await bot(GetFullUserRequest(user.id))
    bio = full.full_user.about or ""
    await bot(functions.account.UpdateProfileRequest(about=bio))

async def set_dp_from_message(msg):
    file_path = await bot.download_media(msg)
    if not file_path:
        return False

    uploaded = await bot.upload_file(file_path)
    await bot(UploadProfilePhotoRequest(file=uploaded))
    os.remove(file_path)
    return True

async def set_dp(user):
    async for p in bot.iter_profile_photos(user.id, limit=1):
        file = await bot.download_media(p)
        uploaded = await bot.upload_file(file)
        await bot(UploadProfilePhotoRequest(file=uploaded))
        os.remove(file)
        return True
    return False

# =====================
# COPY COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.(copyname|copybio|copydp)$"))
async def copy_handler(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()
        user = (await e.get_reply_message()).sender
        cmd = e.pattern_match.group(1)

        if cmd == "copyname":
            await set_name(user)
            text = "✅ Name copied"

        elif cmd == "copybio":
            await set_bio(user)
            text = "✅ Bio copied"

        else:
            ok = await set_dp(user)
            text = "✅ DP copied" if ok else "❌ User has no DP"

        if not SILENT_CLONE:
            m = await bot.send_message(e.chat_id, text)
            await asyncio.sleep(4)
            await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# CLONE SYSTEM
# =====================
async def clone_worker(user, seconds):
    global CLONE_END_TIME
    CLONE_END_TIME = int(time.time()) + seconds

    while time.time() < CLONE_END_TIME:
        await set_name(user)
        await set_bio(user)
        await set_dp(user)
        await asyncio.sleep(10)

@bot.on(events.NewMessage(pattern=r"\.clone (\d+)$"))
async def clone_cmd(e):
    global CLONE_TASK

    if not is_owner(e) or not e.is_reply:
        return

    await e.delete()
    seconds = int(e.pattern_match.group(1))
    user = (await e.get_reply_message()).sender

    if CLONE_TASK and not CLONE_TASK.done():
        CLONE_TASK.cancel()

    CLONE_TASK = asyncio.create_task(clone_worker(user, seconds))

    if not SILENT_CLONE:
        m = await bot.send_message(e.chat_id, f"🧬 Clone started for {seconds}s")
        await asyncio.sleep(4)
        await m.delete()

# =====================
# SILENT CLONE
# =====================
@bot.on(events.NewMessage(pattern=r"\.silentclone (on|off)$"))
async def silent_clone_cmd(e):
    global SILENT_CLONE

    if not is_owner(e):
        return

    await e.delete()
    SILENT_CLONE = e.pattern_match.group(1) == "on"

    m = await bot.send_message(
        e.chat_id,
        "🤫 Silent clone enabled" if SILENT_CLONE else "🔊 Silent clone disabled"
    )
    await asyncio.sleep(4)
    await m.delete()

# =====================
# BACKUP PROFILE
# =====================
@bot.on(events.NewMessage(pattern=r"\.backupprofile(?: (force))?$"))
async def backup_profile_cmd(e):
    if not is_owner(e):
        return

    await e.delete()
    force = bool(e.pattern_match.group(1))

    if profile_col.find_one({"_id": "backup"}) and not force:
        if not SILENT_CLONE:
            m = await bot.send_message(e.chat_id, "⚠️ Backup exists (use force)")
            await asyncio.sleep(4)
            await m.delete()
        return

    me = await bot.get_me()
    full = await bot(GetFullUserRequest(me.id))
    bio = full.full_user.about or ""

    dp_msg_id = None
    async for p in bot.iter_profile_photos(me.id, limit=1):
        file = await bot.download_media(p)
        msg = await bot.send_file("me", file)
        dp_msg_id = msg.id
        os.remove(file)
        break

    profile_col.update_one(
        {"_id": "backup"},
        {"$set": {
            "first_name": me.first_name,
            "last_name": me.last_name,
            "bio": bio,
            "dp_msg_id": dp_msg_id,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }},
        upsert=True
    )

    if not SILENT_CLONE:
        m = await bot.send_message(e.chat_id, "💾 Profile backup saved")
        await asyncio.sleep(4)
        await m.delete()

# =====================
# RESTORE PROFILE
# =====================
@bot.on(events.NewMessage(pattern=r"\.restoreprofile$"))
async def restore_profile(e):
    if not is_owner(e):
        return

    await e.delete()
    data = profile_col.find_one({"_id": "backup"})

    if not data:
        if not SILENT_CLONE:
            m = await bot.send_message(e.chat_id, "❌ No backup found")
            await asyncio.sleep(4)
            await m.delete()
        return

    await bot(functions.account.UpdateProfileRequest(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        about=data.get("bio")
    ))

    if data.get("dp_msg_id"):
        msg = await bot.get_messages("me", ids=data["dp_msg_id"])
        await set_dp_from_message(msg)

    if not SILENT_CLONE:
        m = await bot.send_message(e.chat_id, "♻️ Profile restored")
        await asyncio.sleep(4)
        await m.delete()

# =====================
# BACKUP INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.backupinfo$"))
async def backup_info(e):
    if not is_owner(e):
        return

    await e.delete()
    data = profile_col.find_one({"_id": "backup"})

    if not data:
        msg = await bot.send_message(e.chat_id, "❌ No backup available")
    else:
        msg = await bot.send_message(
            e.chat_id,
            "💾 **Profile Backup Info**\n\n"
            f"👤 Name: {data.get('first_name')} {data.get('last_name')}\n"
            f"📝 Bio: {'Yes' if data.get('bio') else 'No'}\n"
            f"🖼 DP: {'Yes' if data.get('dp_msg_id') else 'No'}\n"
            f"⏰ Time: {data.get('time')}"
        )

    await asyncio.sleep(6)
    await msg.delete()

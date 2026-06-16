import asyncio
import re
from datetime import datetime, timedelta, UTC
from bson import ObjectId
import pytz  # Timezone handling ke liye

from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.auto_delete import auto_delete
from utils.mongo import mongo

PLUGIN_NAME = "scheduler.py"

# Timezone Setup
IST = pytz.timezone("Asia/Kolkata")

def get_ist_now():
    """Returns current time in India (IST)"""
    return datetime.now(IST)

def format_to_ist_12hr(dt_obj):
    """Converts UTC/Naive datetime to IST 12-hour string"""
    if dt_obj.tzinfo is None:
        # Agar naive hai toh usey UTC maan kar IST mein convert karo
        dt_obj = dt_obj.replace(tzinfo=UTC)
    ist_time = dt_obj.astimezone(IST)
    return ist_time.strftime("%Y-%m-%d %I:%M %p")

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ scheduler.py loaded")

# =====================
# MONGO SETUP
# =====================
if mongo is None:
    col = None
else:
    try:
        db = mongo["userbot"]
        col = db["schedules"]
    except Exception:
        col = None

# =====================
# HELP & EXPLAIN
# =====================
register_help(
    "scheduler",
    ".schedule TIME TEXT\n.schedules\n.cancelschedule ID\n\n• Format: 10m, 2h, or YYYY-MM-DD HH:MM"
)

# =====================
# TIME PARSER
# =====================
def parse_time(text: str):
    now_utc = datetime.now(UTC)
    if re.fullmatch(r"\d+m", text):
        return now_utc + timedelta(minutes=int(text[:-1]))
    if re.fullmatch(r"\d+h", text):
        return now_utc + timedelta(hours=int(text[:-1]))
    try:
        # User input ko local (IST) maan kar UTC mein convert karna
        local_dt = datetime.strptime(text, "%Y-%m-%d %H:%M")
        local_dt = IST.localize(local_dt)
        return local_dt.astimezone(UTC)
    except Exception:
        return None

# =====================
# BACKGROUND WORKER
# =====================
async def scheduler_worker():
    if col is None: return
    await asyncio.sleep(10)

    while True:
        try:
            now_utc = datetime.now(UTC)
            tasks = col.find({"run_at": {"$lte": now_utc}, "done": False})

            for task in tasks:
                try:
                    await bot.send_message(task["chat_id"], task["text"])
                    col.update_one({"_id": task["_id"]}, {"$set": {"done": True}})
                except Exception:
                    continue
        except Exception as ex:
            await log_error(bot, PLUGIN_NAME, ex)
        await asyncio.sleep(5)

if col is not None:
    bot.loop.create_task(scheduler_worker())

# =====================
# COMMANDS
# =====================

@bot.on(events.NewMessage(pattern=r"\.schedule(?:\s+([\s\S]+))?$"))
async def schedule_cmd(e):
    if not is_owner(e) or col is None: return
    try:
        await e.delete()
        args = (e.pattern_match.group(1) or "").split(None, 1)
        if len(args) < 2:
            msg = await bot.send_message(e.chat_id, "Usage: `.schedule 10m Message`")
            return await auto_delete(msg, 6)

        when_utc = parse_time(args[0])
        if not when_utc:
            msg = await bot.send_message(e.chat_id, "❌ Format: `10m`, `2h` or `2026-04-12 15:30` (IST)")
            return await auto_delete(msg, 6)

        doc = {
            "chat_id": e.chat_id,
            "text": args[1],
            "run_at": when_utc,
            "done": False,
            "created_at": datetime.now(UTC)
        }
        res = col.insert_one(doc)
        
        # Displaying in IST 12-hour format
        ist_str = format_to_ist_12hr(when_utc)
        msg = await bot.send_message(e.chat_id, f"⏰ **Scheduled**\nID: `{res.inserted_id}`\nAt: `{ist_str}` (IST)")
        await auto_delete(msg, 10)
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

@bot.on(events.NewMessage(pattern=r"\.schedules$"))
async def list_schedules(e):
    if not is_owner(e) or col is None: return
    try:
        await e.delete()
        tasks = list(col.find({"done": False}))
        if not tasks:
            msg = await bot.send_message(e.chat_id, "📭 No pending schedules")
            return await auto_delete(msg, 6)

        text = "📅 **Scheduled Messages (IST)**\n\n"
        for t in tasks:
            ist_time = format_to_ist_12hr(t['run_at'])
            text += f"• `{t['_id']}`\n  └ ⏰ `{ist_time}`\n"

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 20)
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

@bot.on(events.NewMessage(pattern=r"\.cancelschedule(?: (.*))?$"))
async def cancel_schedule(e):
    if not is_owner(e) or col is None: return
    try:
        await e.delete()
        sid = (e.pattern_match.group(1) or "").strip()
        if not sid:
            msg = await bot.send_message(e.chat_id, "Usage: `.cancelschedule ID`")
            return await auto_delete(msg, 6)
        
        col.delete_one({"_id": ObjectId(sid)})
        msg = await bot.send_message(e.chat_id, "✅ Schedule cancelled")
        await auto_delete(msg, 6)
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

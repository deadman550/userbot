# plugins/scheduler.py

import asyncio
import re
from datetime import datetime, timedelta
from bson import ObjectId

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

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ scheduler.py loaded")

# =====================
# MONGO SETUP (SAFE)
# =====================
if mongo is None:
    print("⚠️ MongoDB not connected — scheduler disabled")
    col = None
else:
    try:
        db = mongo["userbot"]
        col = db["schedules"]
    except Exception:
        col = None

# =====================
# HELP
# =====================
register_help(
    "scheduler",
    ".schedule TIME TEXT\n"
    ".schedules\n"
    ".cancelschedule ID\n\n"
    "• Persistent scheduler (MongoDB)\n"
    "• Owner only"
)

# =====================
# EXPLAIN
# =====================
register_explain(
    "scheduler",
    """
⏰ **SCHEDULER**

.schedule 10m Hello  
.schedule 2h Good night  
.schedule 2026-02-01 09:00 Happy Birthday  

.schedules  
.cancelschedule ID  

• Restart safe  
• MongoDB based
"""
)

# =====================
# TIME PARSER
# =====================
def parse_time(text: str):
    if re.fullmatch(r"\d+m", text):
        return datetime.utcnow() + timedelta(minutes=int(text[:-1]))

    if re.fullmatch(r"\d+h", text):
        return datetime.utcnow() + timedelta(hours=int(text[:-1]))

    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M")
    except Exception:
        return None

# =====================
# BACKGROUND WORKER (ULTRA SAFE)
# =====================
async def scheduler_worker():
    if col is None:
        return

    await asyncio.sleep(10)  # startup buffer

    while True:
        try:
            now = datetime.utcnow()

            try:
                tasks = col.find({
                    "run_at": {"$lte": now},
                    "done": False
                })
            except Exception:
                # Mongo temporary issue → wait silently
                await asyncio.sleep(10)
                continue

            for task in tasks:
                try:
                    await bot.send_message(task["chat_id"], task["text"])
                    col.update_one(
                        {"_id": task["_id"]},
                        {"$set": {"done": True}}
                    )
                except Exception:
                    continue

        except Exception as ex:
            # only log, do NOT break plugin
            await log_error(bot, PLUGIN_NAME, ex)

        await asyncio.sleep(5)

# start worker safely
if col is not None:
    bot.loop.create_task(scheduler_worker())

# =====================
# .schedule
# =====================
@bot.on(events.NewMessage(pattern=r"\.schedule(?:\s+([\s\S]+))?$"))
async def schedule_cmd(e):
    if not is_owner(e) or col is None:
        return

    try:
        await e.delete()

        args = (e.pattern_match.group(1) or "").split(None, 1)
        if len(args) < 2:
            msg = await bot.send_message(e.chat_id, "Usage:\n.schedule TIME TEXT")
            return await auto_delete(msg, 6)

        when = parse_time(args[0])
        if not when:
            msg = await bot.send_message(e.chat_id, "❌ Invalid time format")
            return await auto_delete(msg, 6)

        doc = {
            "chat_id": e.chat_id,
            "text": args[1],
            "run_at": when,
            "done": False,
            "created_at": datetime.utcnow()
        }

        try:
            res = col.insert_one(doc)
        except Exception:
            msg = await bot.send_message(
                e.chat_id,
                "❌ MongoDB temporary unavailable. Try again."
            )
            return await auto_delete(msg, 6)

        msg = await bot.send_message(
            e.chat_id,
            f"⏰ **Scheduled**\nID: `{res.inserted_id}`\nAt: `{when}`"
        )
        await auto_delete(msg, 8)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# .schedules
# =====================
@bot.on(events.NewMessage(pattern=r"\.schedules$"))
async def list_schedules(e):
    if not is_owner(e) or col is None:
        return

    try:
        await e.delete()

        try:
            tasks = list(col.find({"done": False}))
        except Exception:
            msg = await bot.send_message(
                e.chat_id,
                "❌ MongoDB temporary unavailable"
            )
            return await auto_delete(msg, 6)

        if not tasks:
            msg = await bot.send_message(e.chat_id, "📭 No pending schedules")
            return await auto_delete(msg, 6)

        text = "📅 **Scheduled Messages**\n\n"
        for t in tasks:
            text += f"• `{t['_id']}` → `{t['run_at']}`\n"

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 15)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# .cancelschedule
# =====================
@bot.on(events.NewMessage(pattern=r"\.cancelschedule(?: (.*))?$"))
async def cancel_schedule(e):
    if not is_owner(e) or col is None:
        return

    try:
        await e.delete()

        sid = (e.pattern_match.group(1) or "").strip()
        if not sid:
            msg = await bot.send_message(e.chat_id, "Usage:\n.cancelschedule ID")
            return await auto_delete(msg, 6)

        try:
            col.delete_one({"_id": ObjectId(sid)})
        except Exception:
            msg = await bot.send_message(
                e.chat_id,
                "❌ Invalid ID or Mongo unavailable"
            )
            return await auto_delete(msg, 6)

        msg = await bot.send_message(e.chat_id, "❌ Schedule cancelled")
        await auto_delete(msg, 6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

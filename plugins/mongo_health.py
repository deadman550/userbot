from telethon import events
from datetime import datetime

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from database import db

print("✔ mongo_health.py loaded")

# =====================
# MONGO HEALTH CHECK
# =====================
def check_mongo_health():
    try:
        db.command("ping")
        return {
            "ok": True,
            "db": db.name,
            "collection": "settings",
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

# =====================
# COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.mongo$"))
async def mongo_health_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except Exception:
            pass

        health = check_mongo_health()

        if health["ok"]:
            text = (
                "🟢 MONGO DB STATUS: CONNECTED\n\n"
                f"Database: {health['db']}\n"
                f"Collection: {health['collection']}\n"
                f"Time: {health['time']}"
            )
        else:
            text = (
                "🔴 MONGO DB STATUS: ERROR\n\n"
                f"Reason:\n{health['error']}"
            )

        msg = await bot.send_message(e.chat_id, text)
        await bot.loop.create_task(_auto_delete(msg, 10))

    except Exception:
        await log_error(bot, "mongo_health.py")

# =====================
# AUTO DELETE (LOCAL)
# =====================
async def _auto_delete(msg, sec):
    import asyncio
    await asyncio.sleep(sec)
    try:
        await msg.delete()
    except Exception:
        pass
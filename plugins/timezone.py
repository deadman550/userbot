# Lightweight Time & Date Plugin - MongoDB Persistent
from telethon import events
from datetime import datetime
import pytz

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.mongo import mongo

PLUGIN_NAME = "timezone.py"

# =====================
# MONGO SETUP
# =====================
if mongo is None:
    col = None
    DEFAULT_TZ = "Asia/Kolkata"
else:
    try:
        db = mongo["userbot"]
        col = db["settings"] # Ek generic settings collection
    except Exception:
        col = None
    DEFAULT_TZ = "Asia/Kolkata"

def get_saved_tz():
    """Database se timezone nikalne ke liye"""
    if col is not None:
        data = col.find_one({"_id": "timezone_config"})
        if data:
            return data.get("tz", "Asia/Kolkata")
    return DEFAULT_TZ

def get_now():
    tz_name = get_saved_tz()
    try:
        tz = pytz.timezone(tz_name)
    except:
        tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz), tz_name

# =====================
# COMMANDS
# =====================

@bot.on(events.NewMessage(pattern=r"\.time$"))
async def show_time(e):
    try:
        now, tz_name = get_now()
        time_str = now.strftime('%I:%M:%S %p').lstrip('0')
        await e.edit(f"🕒 **Current Time**\n`{time_str}`\n🌍 Zone: `{tz_name}`")
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

@bot.on(events.NewMessage(pattern=r"\.date$"))
async def show_date(e):
    try:
        now, tz_name = get_now()
        date_str = now.strftime('%d %B %Y')
        day_str = now.strftime('%A')
        time_str = now.strftime('%I:%M %p').lstrip('0')
        
        await e.edit(
            f"📅 **Current Date**\n"
            f"• `{date_str}`\n"
            f"• `{day_str}`\n"
            f"• `{time_str}`\n"
            f"🌍 Zone: `{tz_name}`"
        )
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

@bot.on(events.NewMessage(pattern=r"\.settz\s+(.+)"))
async def set_timezone(e):
    if col is None:
        return await e.edit("❌ MongoDB not connected. Cannot save permanently.")
    
    try:
        tz_name = e.pattern_match.group(1).strip()
        pytz.timezone(tz_name) # validate
        
        # Database mein update/insert karna
        col.update_one(
            {"_id": "timezone_config"},
            {"$set": {"tz": tz_name}},
            upsert=True
        )
        
        await e.edit(f"✅ **Timezone saved to DB:** `{tz_name}`")
    except Exception as ex:
        await e.edit("❌ Invalid timezone.\nExample: `Asia/Kolkata` or `UTC`.")

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "timezone",
    ".time - Show current time\n"
    ".date - Show full date\n"
    ".settz <zone> - Permanently set zone in DB\n\n"
    "• Restart-safe (MongoDB)"
            )
        

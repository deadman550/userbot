# Lightweight Time & Date Plugin
# Telethon Userbot Compatible

from telethon import events
from datetime import datetime
import pytz

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "timezone.py"
print("✔ timezone.py loaded (Lightweight Time Plugin)")

# default timezone (fallback)
USER_TIMEZONE = "UTC"


def get_time(tz_name):
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)


@bot.on(events.NewMessage(pattern=r"\.settz\s+(.+)"))
async def set_timezone(e):
    global USER_TIMEZONE
    try:
        tz_name = e.pattern_match.group(1).strip()

        # validate timezone
        pytz.timezone(tz_name)

        USER_TIMEZONE = tz_name
        await e.edit(f"✅ **Timezone set to:** `{tz_name}`")

    except Exception:
        await e.edit("❌ Invalid timezone.\nExample: `Asia/Kolkata`")


@bot.on(events.NewMessage(pattern=r"\.tz$"))
async def show_timezone(e):
    await e.edit(f"🌍 **Current Timezone:** `{USER_TIMEZONE}`")


@bot.on(events.NewMessage(pattern=r"\.time$"))
async def show_time(e):
    try:
        now = get_time(USER_TIMEZONE)
        await e.edit(
            f"🕒 **Current Time**\n"
            f"• Timezone: `{USER_TIMEZONE}`\n"
            f"• Time: `{now.strftime('%I:%M:%S %p').lstrip('0')}`"
        )
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)


@bot.on(events.NewMessage(pattern=r"\.date$"))
async def show_date(e):
    try:
        now = get_time(USER_TIMEZONE)
        await e.edit(
            f"📅 **Current Date**\n"
            f"• Timezone: `{USER_TIMEZONE}`\n"
            f"• Date: `{now.strftime('%d %B %Y (%A)')}`\n"
            f"• Time: `{now.strftime('%I:%M %p').lstrip('0')}`"
        )
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "timezone",
    ".settz <timezone>\n"
    ".tz\n"
    ".time\n"
    ".date\n\n"
    "• Lightweight real-time clock\n"
    "• No images, no spam\n"
    "• Uses pytz timezones"
)

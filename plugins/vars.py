import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.vars import (
    set_var,
    get_var,
    del_var,
    all_vars
)

print("✔ vars.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "vars",
    ".setvar KEY VALUE\n"
    ".getvar KEY\n"
    ".delvar KEY\n"
    ".vars\n\n"
    "• Persistent variables\n"
    "• Owner only"
)

# =====================
# SET VAR
# =====================
@bot.on(events.NewMessage(pattern=r"\.setvar (\S+) (.+)"))
async def setvar_cmd(e):
    if not is_owner(e):
        return

    try:
        key = e.pattern_match.group(1).upper()
        value = e.pattern_match.group(2)

        try:
            await e.delete()
        except Exception:
            pass

        set_var(key, value)

        msg = await bot.send_message(
            e.chat_id,
            f"✅ SAVED `{key}`"
        )
        await asyncio.sleep(5)
        await msg.delete()

    except Exception:
        await log_error(bot, "vars.py")


# =====================
# GET VAR
# =====================
@bot.on(events.NewMessage(pattern=r"\.getvar (\S+)"))
async def getvar_cmd(e):
    if not is_owner(e):
        return

    try:
        key = e.pattern_match.group(1).upper()

        try:
            await e.delete()
        except Exception:
            pass

        value = get_var(key)

        if value is None:
            msg = await bot.send_message(e.chat_id, "❌ Not found")
        else:
            msg = await bot.send_message(
                e.chat_id,
                f"`{key}` = `{value}`"
            )

        await asyncio.sleep(10)
        await msg.delete()

    except Exception:
        await log_error(bot, "vars.py")


# =====================
# DELETE VAR
# =====================
@bot.on(events.NewMessage(pattern=r"\.delvar (\S+)"))
async def delvar_cmd(e):
    if not is_owner(e):
        return

    try:
        key = e.pattern_match.group(1).upper()

        try:
            await e.delete()
        except Exception:
            pass

        del_var(key)

        msg = await bot.send_message(
            e.chat_id,
            f"🗑 DELETED `{key}`"
        )
        await asyncio.sleep(5)
        await msg.delete()

    except Exception:
        await log_error(bot, "vars.py")


# =====================
# LIST VARS
# =====================
@bot.on(events.NewMessage(pattern=r"\.vars$"))
async def vars_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except Exception:
            pass

        data = all_vars()

        if not data:
            msg = await bot.send_message(
                e.chat_id,
                "No vars found"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        text = "📦 VARIABLES\n\n"
        for k in sorted(data.keys()):
            text += f"• `{k}`\n"

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception:
        await log_error(bot, "vars.py")
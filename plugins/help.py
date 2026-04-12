from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import get_all_help
from utils.plugin_status import get_broken_plugins
from utils.logger import log_error
from utils.auto_delete import auto_delete

print("✔ help.py loaded")

# Telegram safe limit (real limit ~4096)
MAX_LEN = 3500


# =====================
# SEND LONG TEXT SAFELY
# =====================
async def send_long(e, text, delete_after=40):
    for i in range(0, len(text), MAX_LEN):
        msg = await e.reply(text[i:i + MAX_LEN])
        if delete_after:
            await auto_delete(msg, delete_after)


# =====================
# BUILD MAIN HELP
# =====================
def build_main_help():
    plugins = sorted(get_all_help().keys())

    text = (
        "📘 USERBOT HELP (AUTO)\n\n"
        "Use:\n"
        ".help plugin\n\n"
        "Available plugins:\n"
    )

    for p in plugins:
        text += f"• {p}\n"

    text += (
        "\nExtra:\n"
        ".help all\n"
        ".help broken"
    )

    return text


# =====================
# HELP2 COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.help(?:\s+(.*))?$"))
async def help2_cmd(e):
    if not is_owner(e):
        return

    try:
        # delete command safely
        try:
            await e.delete()
        except:
            pass

        help_data = get_all_help()
        arg = e.pattern_match.group(1)

        # -----------------
        # .help2
        # -----------------
        if not arg:
            msg = await e.reply(build_main_help())
            await auto_delete(msg, 40)
            return

        arg = arg.lower().strip()

        # -----------------
        # .help2 all
        # -----------------
        if arg == "all":
            text = "📚 ALL COMMANDS\n\n"

            for name, section in help_data.items():
                text += (
                    "====================\n"
                    f"{name.upper()}\n"
                    "====================\n"
                    f"{section.strip()}\n\n"
                )

            await send_long(e, text, 40)
            return

        # -----------------
        # .help2 broken
        # -----------------
        if arg == "broken":
            broken = get_broken_plugins()

            if not broken:
                msg = await e.reply("✅ All plugins are working fine")
                await auto_delete(msg, 10)
                return

            text = "🚨 BROKEN PLUGINS\n\n"

            for name, info in broken.items():
                text += (
                    f"❌ {name}\n"
                    f"Error: {info.get('error')}\n"
                    f"Time: {info.get('time')}\n"
                    "--------------------\n"
                )

            await send_long(e, text, 20)
            return

        # -----------------
        # .help <plugin>
        # -----------------
        section = help_data.get(arg)
        if not section:
            msg = await e.reply("❌ Unknown help section")
            await auto_delete(msg, 5)
            return

        await send_long(e, section.strip(), 40)

    except Exception as ex:
        await log_error(bot, "help.py", ex)

import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import get_all_explains, get_explain
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete
from utils.logger import log_error

PLUGIN_NAME = "explanation.py"

print("✔ explanation.py loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "explain",
    ".explain\n"
    ".explain PLUGIN\n\n"
    "• Show detailed explanation of plugins\n"
    "• Auto-registered docs\n"
    "• Owner only"
)

# =====================
# .explain (LIST)
# =====================
@bot.on(events.NewMessage(pattern=r"\.explain$"))
async def explain_list(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        data = get_all_explains()

        if not data:
            msg = await bot.send_message(
                e.chat_id,
                "❌ No plugin explanations registered"
            )
            return await auto_delete(msg, 6)

        text = "📘 **Available Plugin Explanations**\n\n"

        for name in sorted(data.keys()):
            text += f"• `{name}`\n"

        text += "\nUse:\n`.explain plugin_name`"

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 15)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# .explain <plugin>
# =====================
@bot.on(events.NewMessage(pattern=r"\.explain (\w+)$"))
async def explain_plugin(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        name = e.pattern_match.group(1).lower()
        text = get_explain(name)

        if not text:
            msg = await bot.send_message(
                e.chat_id,
                f"❌ No explanation found for `{name}`"
            )
            return await auto_delete(msg, 6)

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 40)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

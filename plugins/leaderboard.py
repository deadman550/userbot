# plugins/leaderboard.py

import asyncio
from telethon import events

from userbot import bot
from utils.leaderboard_helper import load_lb, get_mvp
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.help_registry import register_help

PLUGIN_NAME = "leaderboard.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ leaderboard.py loaded (LEADERBOARD MODE)")

# =====================
# HELP
# =====================
register_help(
    "leaderboard",
    ".battlestats\n"
    ".mvp\n"
    ".mvp battle\n\n"
    "• Global leaderboards\n"
    "• MVP system\n"
)

# =====================
# BATTLESTATS
# =====================
@bot.on(events.NewMessage(pattern=r"\.leaderboard$"))
async def battlestats(e):
    try:
        await e.delete()
        db = load_lb()
        text = ""

        def render_game(title, icon, key):
            nonlocal text
            players = db.get(key, {}).get("players", {})
            text += f"{icon} **{title} LEADERBOARD** 🏆\n\n"

            if not players:
                text += "No battles yet\n\n"
                return

            sorted_players = sorted(
                players.values(),
                key=lambda p: (p["wins"], -p["losses"], p["battles"]),
                reverse=True
            )

            for i, p in enumerate(sorted_players[:5], 1):
                text += (
                    f"**{i}. {p['name']}**\n"
                    f"🏆 {p['wins']} | ❌ {p['losses']} | ⚔ {p['battles']}\n\n"
                )

        render_game("SNAKE", "🐍", "snake")
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        render_game("BATTLE", "⚔️", "battle")
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        render_game("RPS", "✊✋✌️", "rps")
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        render_game("RACE", "🏎", "race")

        m = await e.reply(text)
        await asyncio.sleep(25)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# MVP (SNAKE)
# =====================
@bot.on(events.NewMessage(pattern=r"\.mvp$"))
async def mvp_snake(e):
    try:
        await e.delete()
        best = get_mvp("snake")

        if not best:
            m = await e.reply("🏆 No MVP yet")
            await asyncio.sleep(6)
            await m.delete()
            return

        win_rate = round((best["wins"] / best["battles"]) * 100, 1)

        m = await e.reply(
            "🐍 **SNAKE MVP** 🏆\n\n"
            f"👑 {best['name']}\n"
            f"🏆 {best['wins']} | ❌ {best['losses']} | ⚔ {best['battles']}\n"
            f"📊 Win Rate: {win_rate}%"
        )
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# MVP (BATTLE)
# =====================
@bot.on(events.NewMessage(pattern=r"\.mvp battle$"))
async def mvp_battle(e):
    try:
        await e.delete()
        best = get_mvp("battle")

        if not best:
            m = await e.reply("🏆 No Battle MVP yet")
            await asyncio.sleep(6)
            await m.delete()
            return

        win_rate = round((best["wins"] / best["battles"]) * 100, 1) if best["battles"] else 0

        m = await e.reply(
            "⚔️ **BATTLE MVP** 🏆\n\n"
            f"👑 {best['name']}\n"
            f"🏆 {best['wins']} | ❌ {best['losses']} | ⚔ {best['battles']}\n"
            f"📊 Win Rate: {win_rate}%"
        )
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# plugins/fight.py

import asyncio
import random
from telethon import events

from userbot import bot
from utils.players_helper import get_player, save_players
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fight.py"

# =====================
# PLUGIN LOAD (HEALTH)
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fight.py loaded (BATTLE MODE)")

# =====================
# HELP
# =====================
register_help(
    "battle",
    ".fight (reply)\n\n"
    "• PvP battle game\n"
    "• Stats based (attack / defense / hp)\n"
    "• Coins reward for winner"
)

# =====================
# FIGHT COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.fight$"))
async def fight(e):
    if not e.is_reply:
        return

    try:
        await e.delete()

        me = await e.get_sender()
        opp_msg = await e.get_reply_message()
        opp = await opp_msg.get_sender()

        # ❌ safety checks
        if not opp or me.id == opp.id or opp.bot:
            return

        # load players
        data, p1 = get_player(me.id, me.first_name)
        _, p2 = get_player(opp.id, opp.first_name)

        hp1 = p1.get("hp", 100)
        hp2 = p2.get("hp", 100)

        msg = await e.reply(
            f"⚔️ **BATTLE START** ⚔️\n\n"
            f"🧍 {p1['name']} vs {p2['name']}"
        )

        await asyncio.sleep(1)

        # =====================
        # BATTLE LOOP
        # =====================
        while hp1 > 0 and hp2 > 0:
            dmg1 = max(5, p1["attack"] - p2["defense"] + random.randint(-3, 3))
            dmg2 = max(5, p2["attack"] - p1["defense"] + random.randint(-3, 3))

            hp2 -= dmg1
            hp1 -= dmg2

            hp1 = max(0, hp1)
            hp2 = max(0, hp2)

            await msg.edit(
                f"⚔️ **BATTLE**\n\n"
                f"🧍 {p1['name']} ❤️ `{hp1}`\n"
                f"👤 {p2['name']} ❤️ `{hp2}`"
            )
            await asyncio.sleep(1)

        # =====================
        # RESULT
        # =====================
        if hp1 > hp2:
            winner = p1
        else:
            winner = p2

        winner["coins"] += 20
        save_players(data)

        await msg.edit(
            f"🏆 **WINNER:** {winner['name']}**\n"
            f"💰 +20 Coins"
        )

        await asyncio.sleep(10)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

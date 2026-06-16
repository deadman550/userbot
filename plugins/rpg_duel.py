# plugins/rpg_duel.py

import random
from telethon import events

from userbot import bot
from utils.players_helper import get_player, save_players
from utils.inventory_helper import get_equipped, damage_items, repair_item
from utils.shop_helper import ITEMS
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "rpg_duel.py"
mark_plugin_loaded(PLUGIN_NAME)
print("✔ rpg_duel.py loaded (RPG DUEL MODE)")

# =====================
# HELP
# =====================
register_help(
    "rpg",
    ".challenge (reply)\n"
    ".repair weapon\n"
    ".repair defense\n\n"
    "• RPG duel with base defense\n"
    "• Dynamic repair cost\n"
)

# =====================
# REPAIR COST BY RARITY
# =====================
RARITY_COST = {
    "common": 15,
    "rare": 30,
    "legendary": 50
}

# =====================
# CHALLENGE
# =====================
@bot.on(events.NewMessage(pattern=r"\.challenge$"))
async def challenge(e):
    if not e.is_reply:
        return

    try:
        await e.delete()

        me = await e.get_sender()
        opp_msg = await e.get_reply_message()
        opp = await opp_msg.get_sender()

        data, p1 = get_player(me.id, me.first_name)
        _, p2 = get_player(opp.id, opp.first_name)

        # 🔒 SAFETY FOR OLD USERS
        p1.setdefault("base_defense", {"hp": 100, "max_hp": 100})
        p2.setdefault("base_defense", {"hp": 100, "max_hp": 100})

        eq1 = get_equipped(p1)
        eq2 = get_equipped(p2)

# ✅ get_equipped already returns INT values
        w1 = eq1.get("weapon", 0) or 0
        d1 = eq1.get("defense", 0) or 0

        w2 = eq2.get("weapon", 0) or 0
        d2 = eq2.get("defense", 0) or 0

        atk1 = p1["attack"] + w1
        def1 = p1["defense"] + d1

        atk2 = p2["attack"] + w2
        def2 = p2["defense"] + d2

        dmg1 = max(1, atk1 - def2 + random.randint(-3, 3))
        dmg2 = max(1, atk2 - def1 + random.randint(-3, 3))

        # 🏰 BASE DAMAGE
        p2["base_defense"]["hp"] = max(0, p2["base_defense"]["hp"] - dmg1)
        p1["base_defense"]["hp"] = max(0, p1["base_defense"]["hp"] - dmg2)

        if dmg1 > dmg2:
            winner, loser = p1, p2
        else:
            winner, loser = p2, p1

        winner["coins"] += 15
        loser["coins"] = max(0, loser["coins"] - 10)

        if loser["base_defense"]["hp"] == 0:
            loser["coins"] = max(0, loser["coins"] - 10)

        # ⚙️ DURABILITY DAMAGE
        damage_items(loser, weapon_dmg=10, defense_dmg=8)
        damage_items(winner, weapon_dmg=4, defense_dmg=3)

        save_players(data)

        await e.reply(
            f"⚔️ **RPG DUEL RESULT** ⚔️\n\n"
            f"🥇 Winner: **{winner['name']}** (+15 💰)\n"
            f"💀 Loser: {loser['name']} (-10 💰)\n\n"
            f"🏰 **Base HP**\n"
            f"{p1['name']}: `{p1['base_defense']['hp']}/{p1['base_defense']['max_hp']}`\n"
            f"{p2['name']}: `{p2['base_defense']['hp']}/{p2['base_defense']['max_hp']}`\n\n"
            f"🔧 Use `.repair weapon` or `.repair defense`"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(PLUGIN_NAME, ex)

# =====================
# REPAIR
# =====================
@bot.on(events.NewMessage(pattern=r"\.repair (weapon|defense)$"))
async def repair(e):
    try:
        part = e.pattern_match.group(1)
        user = await e.get_sender()

        data, p = get_player(user.id, user.first_name)
        p.setdefault("base_defense", {"hp": 100, "max_hp": 100})

        eq = get_equipped(p)

        key = eq["weapon_key"] if part == "weapon" else eq["defense_key"]
        if not key:
            await e.reply(f"❌ No {part} equipped")
            return

        item = ITEMS.get(key)
        rarity = item.get("rarity", "common")
        cost = RARITY_COST.get(rarity, 20)

        if p["coins"] < cost:
            await e.reply(f"❌ Need {cost} coins to repair")
            return

        p["coins"] -= cost

        repair_item(p, part, 40)

        if part == "defense":
            p["base_defense"]["hp"] = min(
                p["base_defense"]["max_hp"],
                p["base_defense"]["hp"] + 40
            )

        save_players(data)

        await e.reply(
            f"🔧 **{part.upper()} REPAIRED**\n"
            f"⭐ Rarity: {rarity}\n"
            f"💰 Cost: {cost} coins"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(PLUGIN_NAME, ex)

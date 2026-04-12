# plugins/inventory.py

import asyncio
from telethon import events

from userbot import bot
from utils.players_helper import get_player, save
from utils.shop_helper import ITEMS
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "inventory.py"
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "inventory",
    ".inventory\n"
    ".use <item_key>\n\n"
    "• View items\n"
    "• Use consumables / equip items"
)

# =====================
# VIEW INVENTORY
# =====================
@bot.on(events.NewMessage(pattern=r"\.inventory$"))
async def inventory_view(e):
    try:
        data, p = get_player(e.sender_id, e.sender.first_name)
        inv = p.get("items", {})

        if not inv:
            m = await e.reply("🎒 **Inventory empty**")
            await asyncio.sleep(5)
            await m.delete()
            return

        text = "🎒 **YOUR INVENTORY**\n\n"
        for k, qty in inv.items():
            item = ITEMS.get(k)
            if not item:
                continue
            text += (
                f"• `{k}` → {item['name']} x{qty}\n"
                f"  🏷 {item['rarity']} | 💰 {item['price']}\n\n"
            )

        m = await e.reply(text)
        await asyncio.sleep(20)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# USE ITEM
# =====================
@bot.on(events.NewMessage(pattern=r"\.use (\w+)"))
async def use_item(e):
    try:
        key = e.pattern_match.group(1)

        data, p = get_player(e.sender_id, e.sender.first_name)
        inv = p.get("items", {})

        if key not in inv or inv[key] <= 0:
            m = await e.reply("❌ Item not in inventory")
            await asyncio.sleep(5)
            await m.delete()
            return

        item = ITEMS.get(key)
        if not item:
            return

        # APPLY EFFECT
        p["attack"] += item["attack"]
        p["defense"] += item["defense"]
        p["hp"] = min(100, p["hp"] + item["hp"])

        # CONSUME
        if item["consumable"]:
            inv[key] -= 1
            if inv[key] <= 0:
                del inv[key]

        save(data)

        m = await e.reply(
            f"✅ **ITEM USED**\n\n"
            f"{item['name']}\n"
            f"⚔ +{item['attack']} ATK\n"
            f"🛡 +{item['defense']} DEF\n"
            f"❤️ +{item['hp']} HP"
        )
        await asyncio.sleep(8)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

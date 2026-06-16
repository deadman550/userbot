import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.coins_helper import get_coins, spend
from utils.shop_helper import ITEMS
from utils.players_helper import get_player, save_players
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "shop.py"
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "shop",
    ".coins\n"
    ".shop\n"
    ".buy <item_id>\n"
    ".inventory\n\n"
    "• One global shop\n"
    "• Minigames + Battle items"
)

# =====================
# AUTO DELETE HELPER
# =====================
async def auto_delete(msg, delay):
    await asyncio.sleep(delay)
    await msg.delete()

# =====================
# COINS
# =====================
@bot.on(events.NewMessage(pattern=r"\.coins$"))
async def coins(e):
    try:
        c = get_coins(e.sender_id)
        m = await e.reply(f"💰 **Your Coins:** `{c}`")
        asyncio.create_task(auto_delete(m, 7))

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# SHOP
# =====================
@bot.on(events.NewMessage(pattern=r"\.shop$"))
async def shop(e):
    try:
        text = "🛒 **GLOBAL SHOP** 🛒\n"

        for cat in ["minigame", "battle"]:
            title = "🎮 MINIGAMES ITEMS" if cat == "minigame" else "⚔️ BATTLE ITEMS"
            text += f"\n{title}\n━━━━━━━━━━━━━━━━━━\n"

            for key, item in ITEMS.items():
                if item.get("category") == cat:
                    text += (
                        f"{item['name']}\n"
                        f"🆔 `{key}` | 💰 {item['price']} | ⭐ {item['rarity']}\n"
                    )

                    if item.get("desc"):
                        text += f"📜 {item['desc']}\n"

                    if item.get("ability"):
                        text += "✨ **Abilities:**\n"
                        for ab, val in item["ability"].items():
                            text += f" • `{ab}` → `{val}`\n"

                    text += "\n"

        m = await e.reply(text)
        asyncio.create_task(auto_delete(m, 30))

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BUY ITEM
# =====================
@bot.on(events.NewMessage(pattern=r"\.buy (\w+)$"))
async def buy(e):
    try:
        item_id = e.pattern_match.group(1).lower()
        item = ITEMS.get(item_id)

        if not item:
            m = await e.reply("❌ Item not found")
            asyncio.create_task(auto_delete(m, 7))
            return

        price = item["price"]

        if not spend(e.sender_id, price):
            m = await e.reply("❌ Not enough coins")
            asyncio.create_task(auto_delete(m, 7))
            return

        data, player = get_player(e.sender_id, e.sender.first_name)
        inv = player.setdefault("items", {})
        inv[item_id] = inv.get(item_id, 0) + 1

        save_players(data)

        m = await e.reply(
            f"✅ **Item Purchased!**\n\n"
            f"{item['name']}\n"
            f"💰 Spent: `{price}`\n"
            f"🎒 Added to inventory"
        )
        asyncio.create_task(auto_delete(m, 7))

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

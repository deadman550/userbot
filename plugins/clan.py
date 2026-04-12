# plugins/clan.py

import json
import os
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_control import is_enabled

PLUGIN_NAME = "clan.py"
DB_FILE = "utils/clans.json"

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "clan",
    ". clan create <name>\n"
    ".clan join <name>\n"
    ".clan leave\n"
    ".clan info\n"
    ".clantop\n\n"
    "• Clan system\n"
    "• Team based future PvP\n"
)

# =====================
# DB HELPERS
# =====================
def load_db():
    if not os.path.exists(DB_FILE):
        return {"clans": {}, "users": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

# =====================
# CLAN CREATE
# =====================
@bot.on(events.NewMessage(pattern=r"\.clan create (.+)"))
async def clan_create(e):
    try:
        await e.delete()
        user_id = str(e.sender_id)
        name = e.pattern_match.group(1).strip()

        db = load_db()

        if user_id in db["users"]:
            return await e.reply("❌ You are already in a clan")

        if name in db["clans"]:
            return await e.reply("❌ Clan already exists")

        db["clans"][name] = {
            "owner": user_id,
            "members": [user_id],
            "points": 0
        }
        db["users"][user_id] = name

        save_db(db)
        m = await e.reply(f"🏰 **Clan Created**\n\n👑 {name}")
        await asyncio.sleep(6)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# CLAN JOIN
# =====================
@bot.on(events.NewMessage(pattern=r"\.clan join (.+)"))
async def clan_join(e):
    try:
        await e.delete()
        user_id = str(e.sender_id)
        name = e.pattern_match.group(1).strip()

        db = load_db()

        if user_id in db["users"]:
            return await e.reply("❌ Leave current clan first")

        clan = db["clans"].get(name)
        if not clan:
            return await e.reply("❌ Clan not found")

        clan["members"].append(user_id)
        db["users"][user_id] = name
        save_db(db)

        m = await e.reply(f"✅ Joined clan **{name}**")
        await asyncio.sleep(6)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# CLAN LEAVE
# =====================
@bot.on(events.NewMessage(pattern=r"\.clan leave$"))
async def clan_leave(e):
    try:
        await e.delete()
        user_id = str(e.sender_id)
        db = load_db()

        clan_name = db["users"].get(user_id)
        if not clan_name:
            return await e.reply("❌ You are not in any clan")

        clan = db["clans"][clan_name]
        clan["members"].remove(user_id)
        del db["users"][user_id]

        if not clan["members"]:
            del db["clans"][clan_name]

        save_db(db)
        m = await e.reply("🚪 Left clan")
        await asyncio.sleep(5)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# CLAN INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.clan info$"))
async def clan_info(e):
    try:
        await e.delete()
        user_id = str(e.sender_id)
        db = load_db()

        clan_name = db["users"].get(user_id)
        if not clan_name:
            return await e.reply("❌ You are not in a clan")

        clan = db["clans"][clan_name]

        text = (
            f"🏰 **{clan_name}**\n\n"
            f"👥 Members: `{len(clan['members'])}`\n"
            f"⭐ Points: `{clan['points']}`"
        )

        m = await e.reply(text)
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# CLAN TOP
# =====================
@bot.on(events.NewMessage(pattern=r"\.clantop$"))
async def clan_top(e):
    try:
        await e.delete()
        db = load_db()

        clans = db["clans"]
        if not clans:
            return await e.reply("❌ No clans yet")

        sorted_clans = sorted(
            clans.items(),
            key=lambda c: c[1]["points"],
            reverse=True
        )

        text = "🏆 **TOP CLANS** 🏆\n\n"
        for i, (name, data) in enumerate(sorted_clans[:5], 1):
            text += f"**{i}. {name}** → ⭐ `{data['points']}`\n"

        m = await e.reply(text)
        await asyncio.sleep(20)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

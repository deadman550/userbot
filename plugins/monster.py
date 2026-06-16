from telethon import events
from userbot import bot
from utils.monsters_helper import summon
from utils.players_helper import get_player, save
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded

PLUGIN_NAME = "monsters.py"
mark_plugin_loaded(PLUGIN_NAME)

register_help(
    "monsters",
    ".summon\n"
    ".monster\n\n"
    "• Pokémon-style monsters\n"
)

@bot.on(events.NewMessage(pattern=r"\.summon$"))
async def summon_monster(e):
    data, p = get_player(e.sender_id, e.sender.first_name)
    name, stats = summon()

    p["monster"] = {"name": name, **stats}
    save(data)

    await e.reply(
        f"🐉 **MONSTER SUMMONED**\n\n"
        f"Name: {name}\n"
        f"ATK: {stats['atk']}\n"
        f"DEF: {stats['def']}\n"
        f"Rarity: {stats['rarity'].upper()}"
  )

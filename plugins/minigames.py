import asyncio
import random
import time
from telethon import events
from utils.coins_helper import add_coin

from userbot import bot
from utils.owner import is_owner
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.help_registry import register_help

PLUGIN_NAME = "minigames.py"
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "minigames",
    ".guess <min> <max>\n"
    ".spin\n"
    ".roulette\n"
    ".mathrace\n"
    ".typefast\n"
    ".bomb\n"
    ".react\n\n"
    "• Owner only start\n"
    "• Multiplayer reply based\n"
    "• 30 sec real PvP games"
)

# =====================
# CONFIG
# =====================
GAME_TIME = 30
AUTO_DEL = 5
active_games = {}

# =====================
# TEMP MESSAGE
# =====================
async def temp_reply(chat_id, text, reply_to=None, delay=AUTO_DEL):
    m = await bot.send_message(chat_id, text, reply_to=reply_to)
    await asyncio.sleep(delay)
    await m.delete()

# =====================
# GUESS GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.guess (\d+) (\d+)"))
async def guess_game(e):
    if not is_owner(e):
        return
    try:
        await e.delete()
        lo, hi = map(int, e.pattern_match.groups())
        if lo >= hi:
            return

        ans = random.randint(lo, hi)
        msg = await e.reply(
            f"🎯 **GUESS THE NUMBER**\n\n"
            f"Range: `{lo}-{hi}`\n"
            f"⏱ {GAME_TIME}s\nReply with number"
        )

        active_games[msg.id] = {
            "type": "guess",
            "answer": ans,
            "end": time.time() + GAME_TIME
        }

        await asyncio.sleep(GAME_TIME)
        if msg.id in active_games:
            await msg.reply(f"⏰ Time up!\nAnswer was `{ans}`")
            del active_games[msg.id]

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# SPIN BOTTLE
# =====================
@bot.on(events.NewMessage(pattern=r"\.spin$"))
async def spin_game(e):
    if not is_owner(e):
        return

    await e.delete()
    msg = await e.reply("🍾 **SPIN THE BOTTLE**\n\nReply to join!")

    active_games[msg.id] = {
        "type": "spin",
        "players": set(),
        "end": time.time() + GAME_TIME
    }

    await asyncio.sleep(GAME_TIME)
    game = active_games.pop(msg.id, None)

    if not game or not game["players"]:
        await msg.reply("❌ No players joined")
        return

    uid, name = random.choice(list(game["players"]))
    await msg.reply(f"🍾 Bottle points to 👉 **{name}** 😏")

# =====================
# ROULETTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.roulette$"))
async def roulette_game(e):
    if not is_owner(e):
        return

    await e.delete()
    num = random.randint(0, 9)

    msg = await e.reply(
        "🎰 **ROULETTE**\n\nGuess number `0-9`\n"
        f"⏱ {GAME_TIME}s"
    )

    active_games[msg.id] = {
        "type": "roulette",
        "answer": num,
        "end": time.time() + GAME_TIME
    }

    await asyncio.sleep(GAME_TIME)
    if msg.id in active_games:
        await msg.reply(f"⏰ Time up! Number was `{num}`")
        del active_games[msg.id]

# =====================
# MATH RACE
# =====================
@bot.on(events.NewMessage(pattern=r"\.mathrace$"))
async def mathrace_game(e):
    if not is_owner(e):
        return

    await e.delete()
    a, b = random.randint(10, 50), random.randint(10, 50)
    ans = a + b

    msg = await e.reply(
        f"➕ **MATH RACE**\n\n{a} + {b} = ?\n⏱ {GAME_TIME}s"
    )

    active_games[msg.id] = {
        "type": "math",
        "answer": ans,
        "end": time.time() + GAME_TIME
    }

    await asyncio.sleep(GAME_TIME)
    if msg.id in active_games:
        await msg.reply(f"❌ No winner\nAnswer: `{ans}`")
        del active_games[msg.id]

# =====================
# TYPE FAST
# =====================
@bot.on(events.NewMessage(pattern=r"\.typefast$"))
async def typefast_game(e):
    if not is_owner(e):
        return

    await e.delete()
    word = random.choice(["python", "telegram", "userbot", "telethon", "detor"])

    msg = await e.reply(
        f"⌨️ **TYPE FAST**\n\nType:\n`{word}`\n⏱ {GAME_TIME}s"
    )

    active_games[msg.id] = {
        "type": "type",
        "answer": word,
        "end": time.time() + GAME_TIME
    }

    await asyncio.sleep(GAME_TIME)
    if msg.id in active_games:
        await msg.reply("⏰ Too slow!")
        del active_games[msg.id]

# =====================
# 💣 BOMB GAME (INSTANT CUT WIRE)
# =====================
@bot.on(events.NewMessage(pattern=r"\.bomb$"))
async def bomb_game(e):
    if not is_owner(e):
        return

    await e.delete()

    wires = ["red", "blue", "yellow"]
    safe_wire = random.choice(wires)

    # 😈 40% fake wire (troll)
    fake_wire = None
    if random.random() < 0.4:
        fake_wire = random.choice([w for w in wires if w != safe_wire])

    msg = await e.reply(
        "💣 **CUT THE RIGHT WIRE TO DEFUSE THE BOMB** 💣\n\n"
        "🔴 red\n"
        "🔵 blue\n"
        "🟡 yellow\n\n"
        "✂️ Reply with color name\n"
        "⚠️ One wrong move = BOOM!"
    )

    active_games[msg.id] = {
        "type": "bomb",
        "safe": safe_wire,
        "fake": fake_wire,
        "played": set()   # uid who already tried
    }

# =====================
# UNIVERSAL HANDLER (FIXED)
# =====================
@bot.on(events.NewMessage)
async def game_replies(e):
    if not e.is_reply:
        return

    try:
        r = await e.get_reply_message()
        game = active_games.get(r.id)
        if not game:
            return

        uid = e.sender_id
        name = e.sender.first_name or "User"
        text = e.raw_text.lower().strip()

        # =====================
        # TIMED GAMES ONLY
        # =====================
        if "end" in game and time.time() > game["end"]:
            return

        # ===== GUESS =====
        if game["type"] == "guess" and text.isdigit():
            if int(text) == game["answer"]:
                await e.reply(f"🏆 **WINNER:** {name}\n+10 💰")
                add_coin(uid, name, 10)
                active_games.pop(r.id, None)
            else:
                await temp_reply(e.chat_id, f"❌ Wrong guess, {name}", e.id)

        # ===== ROULETTE =====
        elif game["type"] == "roulette" and text.isdigit():
            if int(text) == game["answer"]:
                await e.reply(f"🎰 **WINNER:** {name}\n+10 💰")
                add_coin(uid, name, 10)
                active_games.pop(r.id, None)

        # ===== MATH =====
        elif game["type"] == "math" and text.isdigit():
            if int(text) == game["answer"]:
                await e.reply(f"➕ **WINNER:** {name}\n+10 💰")
                add_coin(uid, name, 10)
                active_games.pop(r.id, None)

        # ===== TYPE FAST =====
        elif game["type"] == "type" and text == game["answer"]:
            await e.reply(f"⌨️ **FASTEST:** {name}\n+10 💰")
            add_coin(uid, name, 10)
            active_games.pop(r.id, None)

        # ===== SPIN =====
        elif game["type"] == "spin":
            if uid not in {u for u, _ in game["players"]}:
                game["players"].add((uid, name))
                await temp_reply(e.chat_id, f"✅ {name} joined", e.id)

        # =====================
        # 💣 BOMB (INSTANT BLAST MODE)
        # =====================
        elif game["type"] == "bomb" and text in ("red", "blue", "yellow"):

            # ❌ already tried
            if uid in game["played"]:
                return

            game["played"].add(uid)

            # 🧯 REAL SAFE
            if text == game["safe"]:
                await e.reply(f"🧯 **SAFE!** {name} cut `{text}`\n+10 💰")
                add_coin(uid, name, 10)

            # 😈 FAKE SAFE (TROLL)
            elif game["fake"] and text == game["fake"]:
                await e.reply(f"😈 **TROLLED!** {name} trusted fake `{text}` 💥")

            # 💥 BLAST
            else:
                await e.reply(f"💥 **BOOM!** {name} cut `{text}`")

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

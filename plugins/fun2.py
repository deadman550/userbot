# plugins/fun2.py

import asyncio
import random
from telethon import events
from utils.leaderboard_helper import record_match

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun2.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun2.py loaded (FUN + REPLY ANIMATION MODE)")

# =====================
# HELP
# =====================
register_help(
    "fun2",
    ".hack (reply)\n"
    ".hackip (reply)\n"
    ".decrypt (reply)\n"
    ".scan (reply)\n"
    ".rps (reply)\n"
    ".race (reply)\n"
    ".math (reply)\n"
    ".shoot (reply)\n"
    ".pingpong\n"
    ".dice | .coin | .slot | .love\n\n"
    "• Reply-based fun & fake hacking games\n"
    "• Auto delete animations\n"
    "• Just for fun 😄"
)

# =====================
# UTILS
# =====================
async def animate(msg, frames, delay=0.7):
    for f in frames:
        await msg.edit(f)
        await asyncio.sleep(delay)

async def get_target(e):
    if e.is_reply:
        r = await e.get_reply_message()
        u = await r.get_sender()
        return f"🎯 **Target:** {u.first_name or 'User'}\n\n"
    return "🎯 **Target:** Unknown\n\n"

async def auto_cleanup(msg, delay=15):
    await asyncio.sleep(delay)
    await msg.delete()

# =====================
# HACK
# =====================
@bot.on(events.NewMessage(pattern=r"\.hack$"))
async def hack(e):
    try:
        target = await get_target(e)
        await e.delete()

        m = await e.reply("💻 Initializing hack module...")
        frames = [
            f"{target}💻 Connecting █▒▒▒ 10%",
            f"{target}💻 Firewall bypass ███▒ 40%",
            f"{target}💻 Injecting payload █████ 70%",
            f"{target}🔓 ACCESS GRANTED",
            f"{target}✅ **HACK COMPLETE** 😎"
        ]
        await animate(m, frames, 0.8)
        await auto_cleanup(m)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# HACK IP (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.hackip$"))
async def hackip(e):
    try:
        target = await get_target(e)
        await e.delete()

        fake_ip = ".".join(str(random.randint(1,255)) for _ in range(4))
        m = await e.reply("📡 Tracing IP...")

        frames = [
    f"{target}📡 Initializing IP tracer...",
    f"{target}📡 Routing packets ░░░░░░",
    f"{target}📡 Routing packets ███░░░",
    f"{target}🛰 Fetching routing tables...",
    f"{target}🔍 Scanning open ports...",
    f"{target}🔍 Analyzing packet flow...",
    f"{target}⚠️ Firewall detected",
    f"{target}⚠️ Firewall bypassed ✔️",
    f"{target}🌍 Resolving IP address...",
    f"{target}🌍 IP FOUND: `{fake_ip}`",
    f"{target}📍 Locating geographic region...",
    f"{target}📍 Location: Unknown 😏",
    f"{target}✅ **IP TRACE COMPLETE**\n\n"
    f"🌍 IP: `{fake_ip}`\n"
    f"📍 Location: Unknown 😏"
        ]

        await animate(m, frames, 0.9)
        await auto_cleanup(m)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# DECRYPT
# =====================
@bot.on(events.NewMessage(pattern=r"\.decrypt$"))
async def decrypt(e):
    try:
        target = await get_target(e)
        await e.delete()

        m = await e.reply("🔐 Decryption started...")
        frames = [
            f"{target}🔐 AES Loaded",
            f"{target}🔐 Bruteforce ░░░",
            f"{target}🔓 FILE DECRYPTED ✔️"
        ]
        await animate(m, frames, 0.8)
        await auto_cleanup(m)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# SCAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.scan$"))
async def scan(e):
    try:
        target = await get_target(e)
        await e.delete()

        m = await e.reply("🧪 Scanning system...")
        frames = [
            f"{target}🧪 Memory OK",
            f"{target}🧪 Network OK",
            f"{target}🧪 Security OK",
            f"{target}✅ No threats found"
        ]
        await animate(m, frames, 0.6)
        await auto_cleanup(m)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# RPS (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.rps$"))
async def rps(e):
    try:
        await e.delete()

        me = await e.get_sender()
        p1_id = str(me.id)
        p1_name = me.first_name or "Player"

        choices = ["ROCK ✊", "PAPER ✋", "SCISSORS ✌️"]

        # ---------- NON-REPLY (FUN MODE) ----------
        if not e.is_reply:
            bot_choice = random.choice(choices)
            user_choice = random.choice(choices)

            m = await e.reply(
                "✊✋✌️ **RPS (SOLO MODE)**\n\n"
                f"{p1_name}: {user_choice}\n"
                f"Bot 🤖: {bot_choice}\n\n"
                "😄 Just for fun"
            )
            await auto_cleanup(m)
            return

        # ---------- PvP MODE ----------
        r = await e.get_reply_message()
        u = await r.get_sender()
        p2_id = str(u.id)
        p2_name = u.first_name or "Opponent"

        c1 = random.choice(choices)
        c2 = random.choice(choices)

        def winner(a, b):
            if a == b:
                return None
            wins = {
                "ROCK ✊": "SCISSORS ✌️",
                "PAPER ✋": "ROCK ✊",
                "SCISSORS ✌️": "PAPER ✋"
            }
            return a if wins[a] == b else b

        win_choice = winner(c1, c2)

        if win_choice is None:
            m = await e.reply(
                f"✊✋✌️ **RPS DUEL**\n\n"
                f"{p1_name}: {c1}\n"
                f"{p2_name}: {c2}\n\n"
                "🤝 **DRAW**"
            )
            await auto_cleanup(m)
            return

        if win_choice == c1:
            winner_id, winner_name = p1_id, p1_name
            loser_id, loser_name = p2_id, p2_name
        else:
            winner_id, winner_name = p2_id, p2_name
            loser_id, loser_name = p1_id, p1_name

        record_match(
            game="rps",
            winner_id=winner_id,
            winner_name=winner_name,
            loser_id=loser_id,
            loser_name=loser_name
        )

        m = await e.reply(
            f"✊✋✌️ **RPS DUEL**\n\n"
            f"{p1_name}: {c1}\n"
            f"{p2_name}: {c2}\n\n"
            f"🏆 **Winner:** {winner_name}"
        )
        await auto_cleanup(m)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# RACE (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.race$"))
async def race(e):
    try:
        await e.delete()

        me = await e.get_sender()
        p1_id = str(me.id)
        p1_name = me.first_name or "Player"

        # ---------- NON-REPLY (FUN MODE) ----------
        if not e.is_reply:
            winner = random.choice([p1_name, "Bot 🤖"])

            m = await e.reply("🏎 **RACE STARTING...**")
            frames = [
                f"🏎 {p1_name} 💨\n🏎 Bot 🤖",
                f"🏎 {p1_name} 💨💨\n🏎 Bot 🤖 💨",
                f"🏁 **WINNER:** {winner}"
            ]
            for f in frames:
                await m.edit(f)
                await asyncio.sleep(0.7)

            await auto_cleanup(m)
            return

        # ---------- PvP MODE ----------
        r = await e.get_reply_message()
        u = await r.get_sender()
        p2_id = str(u.id)
        p2_name = u.first_name or "Opponent"

        winner_first = random.choice([True, False])

        if winner_first:
            winner_id, winner_name = p1_id, p1_name
            loser_id, loser_name = p2_id, p2_name
        else:
            winner_id, winner_name = p2_id, p2_name
            loser_id, loser_name = p1_id, p1_name

        m = await e.reply("🏎 **RACE STARTING...**")
        frames = [
            f"🏎 {p1_name} 💨\n🏎 {p2_name}",
            f"🏎 {p1_name} 💨💨\n🏎 {p2_name} 💨",
            f"🏁 **WINNER:** {winner_name}"
        ]
        for f in frames:
            await m.edit(f)
            await asyncio.sleep(0.8)

        record_match(
            game="race",
            winner_id=winner_id,
            winner_name=winner_name,
            loser_id=loser_id,
            loser_name=loser_name
        )

        await auto_cleanup(m)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
# =====================
# MATH (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.math$"))
async def math(e):
    target = await get_target(e)
    await e.delete()
    a, b = random.randint(1,50), random.randint(1,50)
    m = await e.reply(f"{target}🧮 Solve:\n**{a} + {b} = ?**")
    await auto_cleanup(m)

# =====================
# SHOOT (REPLY BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.shoot$"))
async def shoot(e):
    target = await get_target(e)
    await e.delete()

    m = await e.reply("🎯 Target locked")
    frames = [
        f"{target}🎯 Aiming",
        f"{target}💥 BOOM",
        f"{target}☠️ Target down"
    ]
    await animate(m, frames, 0.6)
    await auto_cleanup(m)

# =====================
# NON-REPLY SMALL GAMES (UNCHANGED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.dice$"))
async def dice(e):
    await e.reply(f"🎲 Dice: **{random.randint(1,6)}**")

@bot.on(events.NewMessage(pattern=r"\.coin$"))
async def coin(e):
    await e.reply(f"🪙 {random.choice(['HEADS','TAILS'])}")

@bot.on(events.NewMessage(pattern=r"\.slot$"))
async def slot(e):
    s = ["🍒","🍋","⭐","💎"]
    r = [random.choice(s) for _ in range(3)]
    txt = "🎰 " + " | ".join(r)
    if len(set(r)) == 1:
        txt += "\n🎉 JACKPOT!"
    await e.reply(txt)

@bot.on(events.NewMessage(pattern=r"\.love$"))
async def love(e):
    await e.reply(f"❤️ Love Meter: **{random.randint(1,100)}%**")

@bot.on(events.NewMessage(pattern=r"\.pingpong$"))
async def pingpong(e):
    m = await e.reply("🏓 Ping Pong...")
    frames = ["🏓 ●","🏓   ●","🏓      ●","🏁 GG"]
    await animate(m, frames, 0.4)

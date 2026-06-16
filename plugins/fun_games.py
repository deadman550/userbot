import asyncio
import random
from telethon import events
from utils.leaderboard_helper import record_match

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun_games.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun_games.py loaded (GAMES MODE)")

# =====================
# HELP
# =====================
register_help(
    "fungames",
    ".tictac (reply)\n"
    ".battle @user\n"
    ".emojiwar\n"
    ".casino\n"
    ".snake\n"
    ".virus\n\n"
    "• Reply based games\n"
    "• Fake animations\n"
    "• Auto delete commands 😄"
)

# =====================
# COMMON ANIMATION HELPER
# =====================
async def reply_animate(e, frames, delay=0.7):
    if e.is_reply:
        r = await e.get_reply_message()
        m = await r.reply(frames[0])
    else:
        m = await e.reply(frames[0])

    await e.delete()

    for f in frames[1:]:
        await asyncio.sleep(delay)
        await m.edit(f)

# =====================
# TIC TAC TOE (REPLY VS USER)
# =====================
@bot.on(events.NewMessage(pattern=r"\.tictac$"))
async def tictactoe(e):
    try:
        frames = [
            "❌ ⭕ ❌\n⭕ ❌ ⭕\n⬜ ⭕ ❌",
            "❌ ⭕ ❌\n⭕ ❌ ⭕\n❌ ⭕ ❌",
            "🏁 **GAME OVER**\nYou Wins 😎"
        ]
        await reply_animate(e, frames, 0.9)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BATTLE GAME (HP PvP)
# =====================
@bot.on(events.NewMessage(pattern=r"\.battle(?:\s+@?.+)?$"))
async def battle(e):
    try:
        await e.delete()

        me = await e.get_sender()
        p1_id = str(me.id)
        p1_name = me.first_name or "Detor"

        # -------- OPPONENT DETECT --------
        random_win = False

        if e.is_reply:
            r = await e.get_reply_message()
            u = await r.get_sender()
            p2_id = str(u.id)
            p2_name = u.first_name or "Enemy"
            random_win = True

        elif e.pattern_match.group(0).strip() != ".battle":
            username = e.pattern_match.group(0).split()[-1].replace("@", "")
            p2_id = username
            p2_name = username
            random_win = True

        else:
            p2_id = "enemy_bot"
            p2_name = "Enemy 🤖"
            random_win = False  # always you win

        # -------- INIT --------
        hp1, hp2 = 100, 100
        m = await e.reply(f"⚔️ **BATTLE STARTED**\n{p1_name} vs {p2_name}")

        await asyncio.sleep(1)

        # -------- FIGHT LOOP --------
        while hp1 > 0 and hp2 > 0:
            dmg1 = random.randint(8, 20)
            dmg2 = random.randint(8, 20)

            hp2 -= dmg1
            hp1 -= dmg2

            hp1 = max(0, hp1)
            hp2 = max(0, hp2)

            await m.edit(
                f"⚔️ **BATTLE**\n\n"
                f"🧍 {p1_name}: `{hp1}%`\n"
                f"👤 {p2_name}: `{hp2}%`"
            )
            await asyncio.sleep(1)

        # -------- WINNER LOGIC --------
        if random_win:
            p1_win = random.choice([True, False])
        else:
            p1_win = True  # always win vs enemy

        if p1_win:
            winner_id, winner_name = p1_id, p1_name
            loser_id, loser_name = p2_id, p2_name
        else:
            winner_id, winner_name = p2_id, p2_name
            loser_id, loser_name = p1_id, p1_name

        record_match(
            game="battle",
            winner_id=winner_id,
            winner_name=winner_name,
            loser_id=loser_id,
            loser_name=loser_name
        )

        await m.edit(
            f"🏆 **BATTLE RESULT** 🏆\n\n"
            f"🥇 Winner: **{winner_name}**\n"
            f"💀 Loser: {loser_name}\n\n"
            f"📊 Stats saved ✔"
        )

        await asyncio.sleep(12)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# EMOJI WAR
# =====================
@bot.on(events.NewMessage(pattern=r"\.emojiwar$"))
async def emojiwar(e):
    try:
        frames = [
            "😀 😃 😄",
            "😡 😠 🤬",
            "💥 💣 💥",
            "😂 🤣 😂",
            "🏁 **EMOJI WAR OVER**"
        ]
        await reply_animate(e, frames, 0.6)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# CASINO GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.casino$"))
async def casino(e):
    try:
        slots = ["🍒", "🍋", "🍉", "⭐", "💎"]
        result = [random.choice(slots) for _ in range(3)]

        frames = [
            "🎰 Spinning...",
            f"🎰 {' '.join(result)}",
            "🎉 **JACKPOT!**" if len(set(result)) == 1 else "😢 You lost"
        ]
        await reply_animate(e, frames, 1.0)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# FAKE VIRUS PRANK
# =====================
@bot.on(events.NewMessage(pattern=r"\.virus$"))
async def fake_virus(e):
    try:
        frames = [
            "🦠 Virus detected...",
            "🦠 Infecting system...",
            "📂 Deleting files...",
            "⚠️ System unstable...",
            "💥 System crashed...",
            "😈 Just kidding!\n❌ No virus detected"
        ]
        await reply_animate(e, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

                
# =====================
# ADVANCED SNAKE GAME
# =====================

# =====================
# HELPERS
# =====================
def hp_bar(hp):
    blocks = max(0, min(10, hp // 10))
    return "█" * blocks + "░" * (10 - blocks)

# =====================
# SNAKE GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.snake$"))
async def snake_game(e):
    try:
        await e.delete()

        # opponent detect
        if e.is_reply:
            r = await e.get_reply_message()
            u = await r.get_sender()
            opp_id = str(u.id)
            opp_name = u.first_name or "User"
        else:
            opp_id = "anaconda"
            opp_name = "Anaconda 🐍"

        cobra_id = "cobra"
        cobra_name = "King Cobra 🐍"

        # init animation
        m = await e.reply("🐍 **SNAKE BATTLE INITIALIZING...**")
        for f in [
            "🐍 Loading venom modules...",
            "🐍 Preparing arena...",
            "🐍 Calculating abilities...",
            "🐍 **BATTLE STARTING** ⚔️"
        ]:
            await m.edit(f)
            await asyncio.sleep(0.6)

        wins_cobra = 0
        wins_opp = 0

        # ===== BEST OF 3 =====
        for round_no in range(1, 4):
            hp_cobra, hp_opp = 100, 100
            poison_opp = 0

            await m.edit(
                f"🎮 **ROUND {round_no}**\n\n"
                f"🐍 **{cobra_name}**\n`[{hp_bar(hp_cobra)}]` {hp_cobra}%\n\n"
                f"🐍 **{opp_name}**\n`[{hp_bar(hp_opp)}]` {hp_opp}%"
            )
            await asyncio.sleep(1)

            while hp_cobra > 0 and hp_opp > 0:
                attacker = random.choice(["cobra", "opp"])
                dmg = random.randint(10, 20)

                crit = random.random() < 0.25
                poison = random.random() < 0.20
                regen = random.random() < 0.15

                if crit:
                    dmg *= 2

                if attacker == "cobra":
                    hp_opp -= dmg
                    text = f"🐍 {cobra_name} attacks `{opp_name}`"
                    if poison:
                        poison_opp = 2
                else:
                    hp_cobra -= dmg
                    text = f"🐍 {opp_name} attacks {cobra_name}"

                if poison_opp > 0:
                    hp_opp -= 5
                    poison_opp -= 1
                    text += " ☠️ POISON"

                if regen:
                    hp_cobra = min(100, hp_cobra + 5)
                    text += " 💚 REGEN"

                hp_cobra = max(0, hp_cobra)
                hp_opp = max(0, hp_opp)

                await m.edit(
                    f"{text}{' 💥 CRIT' if crit else ''}\n\n"
                    f"🐍 **{cobra_name}**\n`[{hp_bar(hp_cobra)}]` {hp_cobra}%\n\n"
                    f"🐍 **{opp_name}**\n`[{hp_bar(hp_opp)}]` {hp_opp}%"
                )
                await asyncio.sleep(1.2)

            if hp_cobra > hp_opp:
                wins_cobra += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** {cobra_name}")
            else:
                wins_opp += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** {opp_name}")

            await asyncio.sleep(1.4)

        # ===== RECORD MATCH (UNIVERSAL) =====
        if wins_opp > wins_cobra:
            record_match(
                game="snake",
                winner_id=opp_id,
                winner_name=opp_name,
                loser_id=cobra_id,
                loser_name=cobra_name
            )
            winner = opp_name
        else:
            record_match(
                game="snake",
                winner_id=cobra_id,
                winner_name=cobra_name,
                loser_id=opp_id,
                loser_name=opp_name
            )
            winner = cobra_name

        await m.edit(
            f"🏁 **MATCH OVER**\n\n"
            f"🐍 {cobra_name} Wins: `{wins_cobra}`\n"
            f"🐍 {opp_name} Wins: `{wins_opp}`\n\n"
            f"🥇 **FINAL WINNER:** `{winner}`\n"
            f"📊 Stats saved ✔"
        )
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

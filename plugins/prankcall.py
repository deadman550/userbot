# plugins/prankcall.py

import asyncio
import random
from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "prankcall.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ prankcall.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "prankcall",
    ".call trump - Prank call to Donald Trump\n"
    ".call modi - Prank call to Narendra Modi\n"
    ".call putin - Prank call to Vladimir Putin\n\n"
    "• Realistic connection attempts\n"
    "• Randomized results\n"
    "• Owner only"
)

# =====================
# CALL DATA SCRIPTS
# =====================
CALL_DATA = {
    "trump": [
        {"start": "📞 **Calling:** `Donald Trump` 🇺🇸", "connect": "📡 `Connecting to White House secure line...`", "fail": "❌ **Connection Failed:** `Trump is busy in a rally. Try again later!`"},
        {"start": "☎️ **Dialing:** `+1-202-TRUMP-01`", "connect": "🔐 `Bypassing Secret Service encryption...`", "fail": "⚠️ **Error:** `Call rejected by Melania Trump. 🚩`"},
        {"start": "📞 **Initiating Call:** `The President` 👔", "connect": "📡 `Routing via satellite (USA-772)...`", "fail": "🚫 **Line Busy:** `Donald Trump is currently eating a burger. 🍔`"},
        {"start": "📱 **Calling:** `Donnie T.` 🦅", "connect": "🎧 `Waiting for response from Mar-a-Lago...`", "fail": "💔 **Failed:** `Trump blocked your number for being too 'Fake News'. 🤥`"}
    ],
    "modi": [
        {"start": "📞 **Calling:** `Narendra Modi` 🇮🇳", "connect": "📡 `Connecting to PMO India...`", "fail": "❌ **Call Failed:** `Modi ji abhi 'Mann Ki Baat' record kar rahe hain.`"},
        {"start": "☎️ **Dialing:** `+91-PM-MODI-01`", "connect": "🔐 `Securing line via ISRO satellite...`", "fail": "⚠️ **Declined:** `Modi ji yoga kar rahe hain, baad mein call karein. 🧘‍♂️`"},
        {"start": "📞 **Calling:** `Pradhan Mantri` 🚩", "connect": "🎧 `Waiting for response from 7, Lok Kalyan Marg...`", "fail": "🚫 **Busy:** `Modi ji election rally mein busy hain. 🗳️`"}
    ],
    "putin": [
        {"start": "📞 **Calling:** `Vladimir Putin` 🇷🇺", "connect": "📡 `Connecting to Kremlin Bunker...`", "fail": "❌ **Failed:** `Putin is currently training his pet bear. 🐻`"},
        {"start": "☎️ **Dialing:** `+7-MOSCOW-KGB`", "connect": "🔐 `Encrypting signal via Russian Firewall...`", "fail": "⚠️ **Alert:** `Call intercepted by KGB. Better run! 🏃‍♂️💨`"},
        {"start": "📞 **Calling:** `The Tsar` 🏰", "connect": "🎧 `Verifying your DNA for access...`", "fail": "🚫 **Rejected:** `Putin is busy riding a horse shirtless. 🏇`"}
    ]
}

# =====================
# PRANK CALL HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"^\.call\s+(trump|modi|putin)(?:\s|$)"))
async def prank_call_handler(e):
    if not is_owner(e):
        return

    try:
        target = e.pattern_match.group(1).lower()
        sequences = CALL_DATA.get(target)
        
        # Pick a random sequence for the target
        seq = random.choice(sequences)

        # 1. Calling Start
        await e.edit(seq["start"])
        await asyncio.sleep(2.5)

        # 2. Connecting status
        await e.edit(f"{seq['start']}\n{seq['connect']}")
        await asyncio.sleep(3.5)

        # 3. Final Failure Message
        await e.edit(f"{seq['fail']}")

        # Auto delete after 10 seconds
        await asyncio.sleep(10)
        await e.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

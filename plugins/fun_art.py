# plugins/fun_art.py
# ASCII ART + FUN ANIMATIONS
# Converted for Telethon Userbot

import asyncio
from telethon import events
from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun_art.py"
DEFAULTUSER = "ULTROID"

print("✔ fun_art loaded (ASCII ART + FUN ANIMATIONS)")

# =====================
# ASCII ARTS
# =====================
ARTS = {
    "cat": """___________
　　　　　|
　　　　　|
　　　　　|
　　　　　|
　　　　　|
　　　　　|
　／￣￣＼|
＜ ´･ 　　 |＼
　|　３　 | 丶＼
＜ 、･　　|　　＼
　＼＿＿／∪ _ ∪)
　　　　　 Ｕ Ｕ
""",

    "kiler": """_/﹋\\_
(҂`_´)
<,︻╦╤─ ҉ - - - Killer Finished you
_/﹋\\_
""",

    "monster": """▄███████▄
█▄█████▄█
█▼▼▼▼▼█
██________█▌
█▲▲▲▲▲█
█████████
_████
""",

    "pig": """┈┈┏━╮╭━┓┈╭━━━━╮
┈┈┃┏┗┛┓┃╭┫ⓞⓘⓝⓚ┃
┈┈╰┓▋▋┏╯╯╰━━━━╯
┈╭━┻╮╲┗━━━━╮╭╮┈
┈┃▎▎┃╲╲╲╲╲╲┣━╯┈
┈╰━┳┻▅╯╲╲╲╲┃┈┈┈
┈┈┈╰━┳┓┏┳┓┏╯┈┈┈
┈┈┈┈┈┗┻┛┗┻┛┈┈┈┈
""",

    "gun": """░▐█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█▄
░███████████████████████
░▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓◤
░▀░▐▓▓▓▓▓▓▌▀█░░░█▀░
░░░▓▓▓▓▓▓█▄▄▄▄▄█▀░░
░░█▓▓▓▓▓▌░░░░░░░░░░
░▐█▓▓▓▓▓░░░░░░░░░░░
░▐██████▌░░░░░░░░░░
""",

    "dog": """╥━━━━━━━━╭━━╮━━┳
╢╭╮╭━━━━━┫┃▋▋━▅┣
╢┃╰┫┈┈┈┈┈┃┃┈┈╰┫┣
╢╰━┫┈┈┈┈┈╰╯╰┳━╯┣
╢┊┊┃┏┳┳━━┓┏┳┫┊┊┣
╨━━┗┛┗┛━━┗┛┗┛━━┻
""",

    "hello": """╔┓┏╦━╦┓╔┓╔━━╗
║┗┛║┗╣┃║┃║X X║
║┏┓║┏╣┗╣┗╣╰╯║
╚┛┗╩━╩━╩━╩━━╝
""",

    "india": """🇮🇳 PROUD TO BE AN INDIAN 🇮🇳"""
}

# =====================
# ASCII ART COMMAND HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.(cat|kiler|monster|pig|gun|dog|hello|india)$"))
async def art_cmd(e):
    if not (e.is_private or e.is_group):
        return

    cmd = e.pattern_match.group(1)
    art = ARTS.get(cmd)
    if art:
        await e.edit(art)

# =====================
# STUPID ANIMATION
# =====================
@bot.on(events.NewMessage(pattern=r"\.stupid$"))
async def stupid_anim(e):
    if not (e.is_private or e.is_group):
        return

    msg = await e.edit("`...`")
    await asyncio.sleep(0.5)

    frames = [
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n🧠         <(^_^ <)🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n🧠       <(^_^ <)  🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n🧠     <(^_^ <)    🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n🧠   <(^_^ <)      🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n🧠 <(^_^ <)        🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n🧠<(^_^ <)         🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n(> ^_^)>🧠         🗑",
        "YOᑌᖇ ᗷᖇᗩIᑎ ➡️ 🧠\n\n           <(^_^ <)🗑",
    ]

    for f in frames:
        await asyncio.sleep(1)
        await msg.edit(f)

# =====================
# KILER ANIMATION (FIXED – SAFE)
# =====================
@bot.on(events.NewMessage(pattern=r"\.killer(?:\s+(.*))?$"))
async def kiler_anim(e):
    # name fix (space + None safe)
    name = (e.pattern_match.group(1) or "die").strip()

    msg = await e.edit(f"**Ready Commando** __{DEFAULTUSER}....")
    await asyncio.sleep(0.5)

    animation_interval = 0.7
    animation_ttl = range(8)

    animation_chars = [
        "Ｆｉｉｉｉｉｒｅ",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        " <,︻╦╤─ ҉ - \n"
        " _/﹋\\_\n",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        "  <,︻╦╤─ ҉ - -\n"
        " _/﹋\\_\n",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        " <,︻╦╤─ ҉ - - -\n"
        " _/﹋\\_\n",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        "<,︻╦╤─ ҉ - -\n"
        " _/﹋\\_\n",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        " <,︻╦╤─ ҉ - \n"
        " _/﹋\\_\n",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        "  <,︻╦╤─ ҉ - -\n"
        " _/﹋\\_\n",

        f"__**Commando**__ {DEFAULTUSER}\n\n"
        "_/﹋\\_\n"
        " (҂`_´)\n"
        f" <,︻╦╤─ ҉ - - - {name}\n"
        " _/﹋\\_\n",
    ]

    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await msg.edit(animation_chars[i])

# =====================
# HELP
# =====================
register_help(
    "fun_art",
    ".cat .kiler .monster .pig",
    ".gun .dog .hello .india\n"
    ".stupid\n"
    ".killer <name>\n"
    "• ASCII art + fun animations"
  )

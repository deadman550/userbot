# plugins/keyword_scam.py

from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.mongo import settings

PLUGIN = "keyword_scam.py"
print("✔ keyword_scam.py loaded")

# =====================
# HELP
# =====================
register_help(
    "keyword_scam",
    ".keyword on|off\n"
    ".keyword add <word> | <reply>\n"
    ".keyword del <word>\n"
    ".keyword list\n\n"
    ".scamfilter on|off\n"
    ".scamword add <word>\n"
    ".scamword del <word>\n"
    ".scamword list\n\n"
    "• DM only\n"
    "• Owner only\n"
    "• Mongo based"
)

# =====================
# DB HELPERS
# =====================
def get_var(k, d=None):
    doc = settings.find_one({"_id": k})
    return doc["value"] if doc else d

def set_var(k, v):
    settings.update_one({"_id": k}, {"$set": {"value": v}}, upsert=True)

def get_list(k):
    raw = get_var(k, "")
    return [x for x in raw.split("|") if x]

def save_list(k, data):
    set_var(k, "|".join(data))

# =====================
# FLAGS
# =====================
def keyword_on():
    return get_var("KW_ON", "off") == "on"

def scam_on():
    return get_var("SCAM_ON", "off") == "on"

# =====================
# KEYWORD COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.keyword (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("KW_ON", e.pattern_match.group(1))
    await e.reply("✅ Keyword system updated")

@bot.on(events.NewMessage(pattern=r"\.keyword add (.+?) \| (.+)"))
async def _(e):
    if not is_owner(e): return
    data = get_list("KW_LIST")
    data.append(f"{e.pattern_match.group(1)}::{e.pattern_match.group(2)}")
    save_list("KW_LIST", data)
    await e.reply("✅ Keyword added")

@bot.on(events.NewMessage(pattern=r"\.keyword del (.+)"))
async def _(e):
    if not is_owner(e): return
    word = e.pattern_match.group(1).lower()
    data = [x for x in get_list("KW_LIST") if not x.lower().startswith(word + "::")]
    save_list("KW_LIST", data)
    await e.reply("🗑 Keyword removed")

@bot.on(events.NewMessage(pattern=r"\.keyword list"))
async def _(e):
    if not is_owner(e): return
    data = get_list("KW_LIST")
    if not data:
        return await e.reply("📭 No keywords")
    txt = "🔑 **KEYWORDS**\n\n"
    for x in data:
        w, r = x.split("::", 1)
        txt += f"• `{w}` → {r[:30]}...\n"
    await e.reply(txt)

# =====================
# SCAM COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.scamfilter (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("SCAM_ON", e.pattern_match.group(1))
    await e.reply("🚨 Scam filter updated")

@bot.on(events.NewMessage(pattern=r"\.scamword add (.+)"))
async def _(e):
    if not is_owner(e): return
    data = get_list("SCAM_WORDS")
    data.append(e.pattern_match.group(1))
    save_list("SCAM_WORDS", data)
    await e.reply("✅ Scam word added")

@bot.on(events.NewMessage(pattern=r"\.scamword del (.+)"))
async def _(e):
    if not is_owner(e): return
    word = e.pattern_match.group(1).lower()
    data = [x for x in get_list("SCAM_WORDS") if x.lower() != word]
    save_list("SCAM_WORDS", data)
    await e.reply("🗑 Scam word removed")

@bot.on(events.NewMessage(pattern=r"\.scamword list"))
async def _(e):
    if not is_owner(e): return
    data = get_list("SCAM_WORDS")
    if not data:
        return await e.reply("📭 No scam words")
    await e.reply("🚨 **SCAM WORDS**\n\n" + "\n".join(f"• `{x}`" for x in data))

# =====================
# MESSAGE LISTENER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def listener(e):
    try:
        if not e.is_private or is_owner(e):
            return

        text = e.raw_text.lower()

        # KEYWORD
        if keyword_on():
            for k in get_list("KW_LIST"):
                w, r = k.split("::", 1)
                if w.lower() in text:
                    await e.reply(r)
                    return

        # SCAM FILTER
        if scam_on():
            for w in get_list("SCAM_WORDS"):
                if w.lower() in text:
                    await e.reply("⚠️ Please avoid suspicious messages.")
                    return

    except Exception as ex:
        await log_error(bot, PLUGIN, ex)

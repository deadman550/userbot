# plugins/notes.py

import os
import json
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "notes.py"

# =====================
# PATHS
# =====================
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
NOTES_FILE = os.path.join(DATA_DIR, "notes_backup.json")

os.makedirs(DATA_DIR, exist_ok=True)

# =====================
# MEMORY STORE
# =====================
NOTES = {}

# =====================
# LOAD NOTES (IMPORT)
# =====================
def load_notes():
    global NOTES
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                NOTES = json.load(f)
        except Exception:
            NOTES = {}
    else:
        NOTES = {}

# =====================
# SAVE NOTES (EXPORT)
# =====================
def save_notes():
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(NOTES, f, indent=2, ensure_ascii=False)

# load on startup
load_notes()

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ notes.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "notes",
    ".setnote NAME TEXT\n"
    ".getnote NAME\n"
    ".delnote NAME\n"
    ".notes\n\n"
    "• Notes saved locally (file based)\n"
    "• Auto import / export\n"
    "• Railway safe\n"
    "• Owner only"
)

# =====================
# SET NOTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.setnote(?: (.*))?$"))
async def setnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        args = (e.pattern_match.group(1) or "").split(None, 1)

        if len(args) < 2:
            msg = await bot.send_message(e.chat_id, "Usage:\n.setnote NAME TEXT")
            await asyncio.sleep(6)
            return await msg.delete()

        name, text = args
        NOTES[name] = text
        save_notes()

        msg = await bot.send_message(e.chat_id, "✅ Note saved")
        await asyncio.sleep(5)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# GET NOTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.getnote(?: (.*))?$"))
async def getnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        name = (e.pattern_match.group(1) or "").strip()

        if not name:
            msg = await bot.send_message(e.chat_id, "Usage:\n.getnote NAME")
            await asyncio.sleep(6)
            return await msg.delete()

        note = NOTES.get(name)
        if not note:
            msg = await bot.send_message(e.chat_id, "❌ Note not found")
            await asyncio.sleep(5)
            return await msg.delete()

        msg = await bot.send_message(e.chat_id, note)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# DELETE NOTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.delnote(?: (.*))?$"))
async def delnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        name = (e.pattern_match.group(1) or "").strip()

        if not name:
            msg = await bot.send_message(e.chat_id, "Usage:\n.delnote NAME")
            await asyncio.sleep(6)
            return await msg.delete()

        if name in NOTES:
            NOTES.pop(name)
            save_notes()
            msg = await bot.send_message(e.chat_id, "🗑 Note deleted")
        else:
            msg = await bot.send_message(e.chat_id, "❌ Note not found")

        await asyncio.sleep(5)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# LIST NOTES
# =====================
@bot.on(events.NewMessage(pattern=r"\.notes$"))
async def list_notes(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        if not NOTES:
            msg = await bot.send_message(e.chat_id, "📭 No notes saved")
            await asyncio.sleep(6)
            return await msg.delete()

        text = "🗒 **Saved Notes**\n\n"
        for i, name in enumerate(NOTES.keys(), 1):
            text += f"{i}. `{name}`\n"

        text += f"\n📊 Total: {len(NOTES)} notes"

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

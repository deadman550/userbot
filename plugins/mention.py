import asyncio
import random
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "mention.py"
print("✔ mention.py loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# CONFIG
# =====================
BATCH_SIZE = 5
MAX_USERS = 50
DELAY = 3
HISTORY_LIMIT = 300   # fallback message scan

RANDOM_TEXTS = [
    "Kaha ho sab log 🤨",
    "Online bhi aa jao 👀",
    "Attendance lagao 😤",
    "Zinda ho ya nahi 😏",
    "Sab gayab ho kya 😑"
]

# =====================
# STATE (per chat)
# =====================
MENTION_RUNNING = {}
MENTIONED_USERS = {}
MENTION_PROGRESS = {}

# =====================
# HELP
# =====================
register_help(
    "mention",
    ".mention TEXT\n"
    ".rdmention\n"
    ".mentionstatus\n"
    ".stopm\n\n"
    "• Batch mention (5 users)\n"
    "• Flood safe (max 50)\n"
    "• Participant + recent message fallback\n"
    "• Per-chat safe\n"
    "• Owner only"
)

# =====================
# INTERNAL: COLLECT USERS
# =====================
async def collect_users(chat_id: int):
    users = []

    # 1️⃣ Try participants first
    try:
        async for u in bot.iter_participants(chat_id):
            if u.bot or u.deleted:
                continue
            users.append(u)
    except Exception:
        pass

    # 2️⃣ Fallback → recent messages
    if not users:
        async for msg in bot.iter_messages(chat_id, limit=HISTORY_LIMIT):
            if msg.sender and not msg.sender.bot and not msg.sender.deleted:
                users.append(msg.sender)

    # remove duplicates
    uniq = {}
    for u in users:
        uniq[u.id] = u

    return list(uniq.values())

# =====================
# CORE LOGIC
# =====================
async def run_mentions(chat_id: int, base_text: str):
    MENTION_RUNNING[chat_id] = True
    MENTIONED_USERS.setdefault(chat_id, set())
    MENTION_PROGRESS[chat_id] = 0

    batch = []
    count = 0

    try:
        users = await collect_users(chat_id)

        for user in users:
            if not MENTION_RUNNING.get(chat_id):
                break

            if user.id in MENTIONED_USERS[chat_id]:
                continue

            MENTIONED_USERS[chat_id].add(user.id)
            MENTION_PROGRESS[chat_id] += 1
            count += 1

            name = user.first_name or "User"
            batch.append(f"[{name}](tg://user?id={user.id})")

            if len(batch) == BATCH_SIZE:
                await bot.send_message(
                    chat_id,
                    f"{base_text}\n\n" + " ".join(batch),
                    link_preview=False
                )
                batch.clear()
                await asyncio.sleep(DELAY)

            if count >= MAX_USERS:
                break

        if batch and MENTION_RUNNING.get(chat_id):
            await bot.send_message(
                chat_id,
                f"{base_text}\n\n" + " ".join(batch),
                link_preview=False
            )

        msg = await bot.send_message(chat_id, "✅ Mention completed")
        await auto_delete(msg, 6)

    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(bot, PLUGIN_NAME, e)

    finally:
        MENTION_RUNNING[chat_id] = False

# =====================
# .mention
# =====================
@bot.on(events.NewMessage(pattern=r"\.mention (.+)"))
async def mention_cmd(e):
    if not is_owner(e):
        return

    chat_id = e.chat_id
    if MENTION_RUNNING.get(chat_id):
        return

    try:
        await e.delete()
    except:
        pass

    text = e.pattern_match.group(1)
    asyncio.create_task(run_mentions(chat_id, text))

# =====================
# .rdmention
# =====================
@bot.on(events.NewMessage(pattern=r"\.rdmention$"))
async def rdmention_cmd(e):
    if not is_owner(e):
        return

    chat_id = e.chat_id
    if MENTION_RUNNING.get(chat_id):
        return

    try:
        await e.delete()
    except:
        pass

    text = random.choice(RANDOM_TEXTS)
    asyncio.create_task(run_mentions(chat_id, text))

# =====================
# .mentionstatus
# =====================
@bot.on(events.NewMessage(pattern=r"\.mentionstatus$"))
async def mention_status(e):
    if not is_owner(e):
        return

    chat_id = e.chat_id
    running = MENTION_RUNNING.get(chat_id, False)
    count = MENTION_PROGRESS.get(chat_id, 0)

    try:
        await e.delete()
    except:
        pass

    text = (
        "🟢 Mention running\n"
        f"👥 Mentioned: {count}"
        if running else
        "⚪ No active mention"
    )

    msg = await bot.send_message(chat_id, text)
    await auto_delete(msg, 6)

# =====================
# .stopm
# =====================
@bot.on(events.NewMessage(pattern=r"\.stopm$"))
async def stop_mention(e):
    if not is_owner(e):
        return

    chat_id = e.chat_id
    MENTION_RUNNING[chat_id] = False

    try:
        await e.delete()
    except:
        pass

    msg = await bot.send_message(chat_id, "🛑 Mention stopped")
    await auto_delete(msg, 6)

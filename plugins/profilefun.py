import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ profilefun.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "profilefun",
    ".whoami\n"
    "Shows your name & ID\n\n"
    ".status\n"
    "Fake online status\n\n"
    ".hack (reply)\n"
    "Fun hacking animation"
)

# =====================
# HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.(whoami|status|hack)$"))
async def profile_fun(e):
    if not is_owner(e):
        return

    try:
        # delete command safely
        try:
            await e.delete()
        except Exception:
            pass

        cmd = e.pattern_match.group(1)
        text = None  # IMPORTANT

        # =====================
        # WHOAMI
        # =====================
        if cmd == "whoami":
            me = await bot.get_me()
            text = (
                f"👤 You are {me.first_name}\n"
                f"🆔 ID: {me.id}"
            )

        # =====================
        # STATUS
        # =====================
        elif cmd == "status":
            text = "🟢 Status: Online\n⚡ Power: Unlimited"

        # =====================
        # HACK (reply based)
        # =====================
        elif cmd == "hack":
            if not e.is_reply:
                warn = await bot.send_message(
                    e.chat_id,
                    "Reply to a user to hack 😈"
                )
                await asyncio.sleep(3)
                await warn.delete()
                return

            r = await e.get_reply_message()
            if not r or not r.sender_id:
                return

            # Markdown-safe mention (no < >)
            target = f"[User](tg://user?id={r.sender_id})"

            msg = await bot.send_message(
                e.chat_id,
                f"💻 Hacking {target}..."
            )
            await asyncio.sleep(1)

            await msg.edit("📂 Accessing files...")
            await asyncio.sleep(1)

            await msg.edit("🔓 Bypassing security...")
            await asyncio.sleep(1)

            await msg.edit("✅ Hack completed 😈")
            await asyncio.sleep(5)
            await msg.delete()
            return  # IMPORTANT

        # =====================
        # SEND RESULT
        # =====================
        if not text:
            return

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(6)
        await msg.delete()

    except Exception:
        await log_error(bot, "profilefun.py")
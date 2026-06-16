import os
import shutil
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.auto_delete import auto_delete

print("✔ diskclean.py loaded")

# =====================
# HELP REGISTRATION
# =====================
register_help(
    "diskclean",
    ".diskusage\n"
    "Show disk usage only\n\n"
    ".diskclean --dry\n"
    "Preview disk clean (no delete)\n\n"
    ".diskclean confirm\n"
    "Clean disk with confirmation\n\n"
    "Folders affected:\n"
    "• saved_media\n"
    "• assets/tmp"
)

# =====================
# CONFIG
# =====================
CLEAN_FOLDERS = [
    "saved_media",
    "assets/tmp"
]

# =====================
# HELPERS
# =====================
def get_folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

def format_mb(size):
    return round(size / (1024 * 1024), 2)

def calculate_usage():
    total = 0
    details = {}
    for folder in CLEAN_FOLDERS:
        if os.path.isdir(folder):
            size = get_folder_size(folder)
            details[folder] = size
            total += size
        else:
            details[folder] = 0
    return total, details

# =====================
# DISK USAGE
# =====================
@bot.on(events.NewMessage(pattern=r"\.diskusage$"))
async def disk_usage_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        total, details = calculate_usage()

        text = "📊 DISK USAGE\n\n"
        for f, size in details.items():
            text += f"• {f}: {format_mb(size)} MB\n"

        text += f"\nTotal: {format_mb(total)} MB"

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 12)

    except Exception as ex:
        await log_error(bot, "diskclean.py", ex)

# =====================
# DISK CLEAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.diskclean(?: (.*))?$"))
async def disk_clean_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        arg = (e.pattern_match.group(1) or "").strip()

        before_total, before_details = calculate_usage()

        # -----------------
        # DRY RUN
        # -----------------
        if arg == "--dry":
            text = "🧪 DISK CLEAN PREVIEW\n\n"
            for f, size in before_details.items():
                text += f"• {f}: {format_mb(size)} MB\n"

            text += (
                f"\nTotal reclaimable: {format_mb(before_total)} MB\n\n"
                "ℹ️ No files were deleted"
            )

            msg = await bot.send_message(e.chat_id, text)
            await auto_delete(msg, 15)
            return

        # -----------------
        # CONFIRM REQUIRED
        # -----------------
        if arg != "confirm":
            msg = await bot.send_message(
                e.chat_id,
                "⚠️ Confirmation required\n\n"
                "Use:\n"
                ".diskclean confirm\n\n"
                "Or preview:\n"
                ".diskclean --dry"
            )
            await auto_delete(msg, 10)
            return

        # -----------------
        # CLEAN PROCESS
        # -----------------
        cleaned = []
        skipped = []

        for folder in CLEAN_FOLDERS:
            if os.path.isdir(folder):
                try:
                    shutil.rmtree(folder)
                    os.makedirs(folder, exist_ok=True)
                    cleaned.append(folder)
                except:
                    skipped.append(folder)
            else:
                skipped.append(folder)

        after_total, _ = calculate_usage()
        freed = before_total - after_total

        # -----------------
        # REPORT
        # -----------------
        text = "🧹 DISK CLEAN REPORT\n\n"
        text += (
            f"Before: {format_mb(before_total)} MB\n"
            f"After: {format_mb(after_total)} MB\n"
            f"Freed: {format_mb(freed)} MB\n\n"
        )

        if cleaned:
            text += "✅ Cleaned:\n"
            for f in cleaned:
                text += f"• {f}\n"

        if skipped:
            text += "\n⚠️ Skipped:\n"
            for f in skipped:
                text += f"• {f}\n"

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 15)

    except Exception as ex:
        await log_error(bot, "diskclean.py", ex)

import os
import asyncio
import aiohttp
from telethon import events
from telethon.tl.types import DocumentAttributeAudio

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

# =====================
# CONFIGURATION
# =====================
PLUGIN_NAME = "song.py"
API_BASE_URL = "https://rohit-music-downloader-api.vercel.app/search?song="

print(f"✔ {PLUGIN_NAME} loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "song",
    "**Music Downloader:**\n"
    ".song <song name>\n\n"
    "• Searches and directly uploads the song to Telegram.\n"
    "• Owner only"
)

# =====================
# SONG DOWNLOAD COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.song(?:\s+(?P<query>.+))?"))
async def song_cmd(e):
    if not is_owner(e):
        return

    query = e.pattern_match.group("query")

    if not query:
        await e.delete()
        fail_msg = await bot.send_message(e.chat_id, "ℹ **Usage:** `.song <song name>` (e.g., `.song sanam re`)")
        await asyncio.sleep(4)
        await fail_msg.delete()
        return

    try:
        await e.delete()
        status_msg = await bot.send_message(e.chat_id, f"🔍 **Searching for:** `{query}`...")

        # 1. Fetching Data from API
        async with aiohttp.ClientSession() as session:
            async with session.get(API_BASE_URL + query) as response:
                if response.status != 200:
                    await status_msg.edit("❌ **API Error:** Music server is currently down.")
                    return
                
                data = await response.json()

        # 2. Checking if song exists
        if not data.get("success") or not data.get("results"):
            await status_msg.edit(f"❌ **Not Found:** Koi gaana nahi mila `{query}` ke liye.")
            return

        # Top result (first song) uthayenge
        first_song = data["results"][0]
        title = first_song.get("title", "Unknown Title")
        artist = first_song.get("artists", "Unknown Artist")
        duration_str = first_song.get("duration", "0:00")
        download_url = first_song.get("download_url")

        if not download_url:
            await status_msg.edit("❌ **Download Link Missing:** API ne link generate nahi kiya.")
            return

        await status_msg.edit(f"📥 **Downloading:** `{title}`\n🎤 **Artist:** `{artist}`\n⚡ Please wait...")

        # 3. Downloading the file locally
        # .m4a extension use kar rahe hain taaki Telegram isko Audio track mane
        file_name = f"{title.replace('/', '_')}.m4a"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as resp:
                if resp.status == 200:
                    with open(file_name, 'wb') as f:
                        # Chunk by chunk download for better memory management
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                else:
                    await status_msg.edit("❌ **Download Failed:** Server ne file block kar di.")
                    return

        await status_msg.edit("📤 **Uploading to Telegram...**")

        # Duration string (e.g., "5:08") ko seconds me convert karna
        try:
            mins, secs = map(int, duration_str.split(':'))
            duration_seconds = mins * 60 + secs
        except Exception:
            duration_seconds = 0

        # 4. Uploading to Telegram
        caption = (
            f"🎵 **Title:** `{title}`\n"
            f"🎤 **Artist:** `{artist}`\n"
            f"⏱ **Duration:** `{duration_str}`"
        )

        await bot.send_file(
            e.chat_id,
            file_name,
            caption=caption,
            attributes=[
                DocumentAttributeAudio(
                    duration=duration_seconds,
                    title=title,
                    performer=artist
                )
            ]
        )

        # 5. Clean up (Delete the temp message and downloaded file)
        await status_msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
        if 'status_msg' in locals():
            await status_msg.edit(f"❌ **Error:** `{str(ex)}`")

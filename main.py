# main.py
import asyncio
import os

from userbot import bot
from loader import load_plugins
from utils.auto_delete import auto_delete

async def main():
    print("🚀 Starting userbot...")

    # 1️⃣ LOGIN FIRST
    await bot.start()
    print("✅ Userbot logged in")

    # 2️⃣ LOAD PLUGINS AFTER LOGIN
    load_plugins()
    print("✅ Plugins loaded")

    # 3️⃣ OPTIONAL RESTART MESSAGE
    restart_chat = os.environ.pop("RESTART_CHAT", None)
    if restart_chat:
        try:
            msg = await bot.send_message(
                int(restart_chat),
                "✅ Restarted successfully"
            )
            asyncio.create_task(auto_delete(msg, 5))
        except Exception as e:
            print("Restart msg failed:", e)

    # 4️⃣ KEEP PROCESS ALIVE
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

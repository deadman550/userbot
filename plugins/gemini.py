import asyncio
import google.generativeai as genai
import google.ai.generativelanguage as gapic # Version check ke liye
from telethon import events
from userbot import bot
from utils.owner import is_owner

# =====================
# HARDCODED CONFIG
# =====================
TEST_GEMINI_KEY = "AIzaSyCJsC2ZN8DV85VFAjoin75kT_xMms1bdUM"
genai.configure(api_key=TEST_GEMINI_KEY)

@bot.on(events.NewMessage(pattern=r"\.aitest(?:\s+([\s\S]+))?$"))
async def gemini_testing(e):
    if not is_owner(e): return
    
    # 1. Improved Text Detection
    query = e.pattern_match.group(1)
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
    
    if not query:
        return await e.edit("`❌ Bhai, kuch toh likho ya reply karo!`")

    # 2. Check Library Version
    try:
        import pkg_resources
        lib_version = pkg_resources.get_distribution("google-generativeai").version
    except:
        lib_version = "Unknown"

    await e.edit(f"`⚡ Running Test...\n📦 Lib Version: {lib_version}\n🔍 Query: {query[:15]}`")

    # 3. Try Only the most basic path
    try:
        # Ekdum simple initialization
        model = genai.GenerativeModel('gemini-pro') 
        response = await asyncio.to_thread(model.generate_content, query)
        
        if response and response.text:
            await e.edit(f"✅ **Success with Gemini-Pro!**\n\n{response.text}")
        else:
            await e.edit("❌ **API ne response khali bheja hai.**")
            
    except Exception as ex:
        err = str(ex)
        await e.edit(
            f"❌ **Sab Fail Ho Gaya!**\n\n"
            f"**Lib Version:** `{lib_version}`\n"
            f"**Error:** `{err}`\n\n"
            f"**Fix:** Railway Variables mein `PYTHON_VERSION` ko `3.10` set karo aur Requirements mein `google-generativeai==0.8.3` likho."
        )

from utils.help_registry import register_help
register_help("aitest", ".aitest - Final debug with version check")
    

import asyncio
import google.generativeai as genai
from telethon import events
from userbot import bot
from utils.owner import is_owner

# =====================
# HARDCODED CONFIG
# =====================
TEST_GEMINI_KEY = "AIzaSyCJsC2ZN8DV85VFAjoin75kT_xMms1bdUM"

# Configuration
genai.configure(api_key=TEST_GEMINI_KEY)

async def get_working_model(query):
    """Sare possible models try karega jo aapki library support karti ho"""
    # Order: Latest -> Stable -> Legacy
    test_models = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-pro']
    
    for m_name in test_models:
        try:
            model = genai.GenerativeModel(model_name=m_name)
            # Dummy call to check if model exists
            response = await asyncio.to_thread(model.generate_content, query)
            return response.text, m_name
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                continue # Agla model try karo
            return f"API_ERROR: {str(e)}", None
    return "NOT_FOUND", None

@bot.on(events.NewMessage(pattern=r"\.aitest(?:\s+([\s\S]+))?$"))
async def gemini_testing(e):
    if not is_owner(e): return
    
    query = e.pattern_match.group(1) or (await e.get_reply_message()).text if e.is_reply else None
    if not query:
        return await e.edit("`Bhai, kuch text toh dalo!`")

    await e.edit("`⚡ Checking supported Gemini models on this server...`")

    ans, successful_model = await get_working_model(query)

    if successful_model:
        await e.edit(f"✅ **Gemini Test Success!**\n**Model Path:** `{successful_model}`\n\n{ans}")
    elif ans == "NOT_FOUND":
        await e.edit("❌ **Error:** Aapki `google-generativeai` library bahut purani hai. Requirements mein `==0.8.3` karke Clear Cache deploy karo.")
    else:
        await e.edit(f"❌ **Direct API Error:**\n`{ans}`")

from utils.help_registry import register_help
register_help("aitest", ".aitest <query> - Smart Hardcoded Gemini Test")
    

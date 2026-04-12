import asyncio
import google.generativeai as genai
from telethon import events
from userbot import bot
from utils.owner import is_owner

# =====================
# HARDCODED CONFIG (FOR TEST)
# =====================
TEST_GEMINI_KEY = "AIzaSyCJsC2ZN8DV85VFAjoin75kT_xMms1bdUM" # <--- Yahan apni key dalo
TEST_MODEL_NAME = "gemini-1.5-flash-latest"   # <--- Ye hamesha stable rehta hai

# Configuration
genai.configure(api_key=TEST_GEMINI_KEY)
model = genai.GenerativeModel(model_name=TEST_MODEL_NAME)

@bot.on(events.NewMessage(pattern=r"\.aitest(?:\s+([\s\S]+))?$"))
async def gemini_testing(e):
    if not is_owner(e): return
    
    # Input pick karo (Text ya Reply)
    query = e.pattern_match.group(1)
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
        
    if not query:
        return await e.edit("`Bhai, kuch likho toh sahi test karne ke liye!`")

    # Step 1: Edit message to show processing
    await e.edit("`⚡ Gemini Hardcoded Test in progress...`")

    try:
        # Step 2: API Call (Using Thread for non-blocking)
        response = await asyncio.to_thread(
            model.generate_content, 
            query
        )
        
        if response and response.text:
            final_ans = response.text
            # Step 3: Final Edit with result
            await e.edit(f"✅ **Gemini Test Success!**\n\n{final_ans}")
        else:
            await e.edit("❌ **API Success but empty response.** Check Safety Settings.")
            
    except Exception as ex:
        # Step 4: Detail Error dekhne ke liye
        error_msg = str(ex)
        if "API_KEY_INVALID" in error_msg:
            await e.edit("❌ **Error:** API Key galat hai bhai.")
        elif "404" in error_msg:
            await e.edit("❌ **Error:** Model name (1.5-flash-latest) nahi mila.")
        else:
            await e.edit(f"❌ **Direct API Error:**\n`{error_msg}`")

# Help Registry (Optional for test)
from utils.help_registry import register_help
register_help("aitest", ".aitest <query> - Direct Hardcoded Gemini Test")

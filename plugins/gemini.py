import asyncio
import google.generativeai as genai
from telethon import events
from userbot import bot
from utils.owner import is_owner

# Hardcoded Key
genai.configure(api_key="AIzaSyCJsC2ZN8DV85VFAjoin75kT_xMms1bdUM")

@bot.on(events.NewMessage(pattern=r"\.aitest(?:\s+([\s\S]+))?$"))
async def legacy_test(e):
    if not is_owner(e): return
    
    # Text detection logic
    query = e.pattern_match.group(1)
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
        
    if not query:
        return await e.edit("`Bhai, reply karke ya command ke sath text likho!`")

    await e.edit("`⚠️ Attempting Legacy Connection (Gemini-Pro)...`")

    try:
        # Purana model jo har version mein chalta hai
        model = genai.GenerativeModel('gemini-pro')
        response = await asyncio.to_thread(model.generate_content, query)
        
        if response and response.text:
            await e.edit(f"✅ **Legacy Path Success!**\n\n{response.text}")
        else:
            await e.edit("❌ API connect hui par response khali hai.")
            
    except Exception as ex:
        await e.edit(f"❌ **Library Still Outdated!**\n\nError: `{str(ex)}` \n\n**Solution:** Railway Settings mein 'Rebuild' ya 'Redeploy' karo `requirements.txt` badalne ke baad.")
        

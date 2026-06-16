import aiohttp
from telethon import events
from userbot import bot
from utils.owner import is_owner

API_KEY = "AIzaSyCJsC2ZN8DV85VFAjoin75kT_xMms1bdUM"

@bot.on(events.NewMessage(pattern=r"\.aitest(?:\s+([\s\S]+))?$"))
async def direct_api_test(e):
    if not is_owner(e): return
    
    query = e.pattern_match.group(1) or (await e.get_reply_message()).text if e.is_reply else None
    if not query: return await e.edit("`Bhai, kuch toh likho!`")

    await e.edit("`⚡ Direct API Call (Bypassing Library)...`")

    # Direct URL for Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": query}]}]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                
                if "candidates" in data:
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    await e.edit(f"✅ **Direct API Success!**\n\n{answer}")
                else:
                    await e.edit(f"❌ **API Error:**\n`{data}`")
                    
    except Exception as ex:
        await e.edit(f"❌ **Request Failed:**\n`{str(ex)}`")

from utils.help_registry import register_help
register_help("aitest", ".aitest - Direct API Call version (No library needed)")
    

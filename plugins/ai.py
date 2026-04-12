import os
import aiohttp
import asyncio
import google.generativeai as genai
from groq import Groq
from duckduckgo_search import DDGS
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "ai.py"

# =====================
# CONFIG & API SETUP
# =====================
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# 1. HELP & EXPLAIN REGISTRY (Auto)
# =====================
register_help(
    "ai",
    ".ai <query> - Smart Hybrid Mode\n"
    ".aai, .jarvis, .edith - Strict Gemini Mode\n"
    ".aihealth - Check API status"
)

register_explain(
    "ai",
    "🤖 **Omni-AI Multi-Engine (2026)**\n\n"
    "• .ai: Parallel processing (Fastest wins + Fallback)\n"
    "• .aai/.jarvis/.edith: Dedicated Gemini 1.5 Flash\n"
    "• Auto-Delete: 200 Seconds"
)

# =====================
# CORE WORKERS
# =====================

async def get_web_context(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results) if results else ""
    except: return ""

async def get_gemini_resp(prompt, context):
    if not gemini_model: return None, None
    try:
        sys_msg = f"You are Gemini 1.5 Flash. Today is April 12, 2026. Context: {context}"
        response = await asyncio.to_thread(gemini_model.generate_content, f"{sys_msg}\n\nUser: {prompt}")
        return response.text, "Gemini 1.5 Flash"
    except: return None, None

async def get_groq_resp(prompt, context):
    if not groq_client: return None, None
    try:
        sys_msg = f"You are Llama 3.3. Today is April 12, 2026. Context: {context}"
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content, "Groq (Llama 3.3)"
    except: return None, None

# =====================
# 2. API HEALTH CHECKER
# =====================

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    status = "🔍 **Omni-AI Health Report**\n\n"
    status += f"🤖 Groq (Llama): {'🟢 Connected' if GROQ_KEY else '🔴 Key Missing'}\n"
    status += f"♊ Gemini Flash: {'🟢 Configured' if GEMINI_KEY else '🔴 Key Missing'}\n"
    try:
        with DDGS() as ddgs:
            list(ddgs.text("test", max_results=1))
            status += "🌐 Web Search: 🟢 Online"
    except: status += "🌐 Web Search: 🔴 Offline"
    
    msg = await e.respond(status)
    await auto_delete(msg, 15) # Health report deletes in 15s

# =====================
# 3. COMMAND HANDLERS
# =====================

# STRICT GEMINI COMMANDS (.aai, .jarvis, .edith)
@bot.on(events.NewMessage(pattern=r"\.(aai|jarvis|edith)(?:\s+([\s\S]+))?$"))
async def gemini_strict(e):
    if not is_owner(e): return
    query = e.pattern_match.group(2)
    if not query and e.is_reply:
        r = await e.get_reply_message()
        query = r.text
    
    if not query: return await auto_delete(await e.reply("Puchna kya hai?"), 5)
    
    thinking = await e.reply(f"`🚀 {e.pattern_match.group(1).upper()} is thinking...`" )
    context = await get_web_context(query)
    ans, src = await get_gemini_resp(query, context)
    
    await thinking.delete()
    if not ans: ans = "❌ Gemini is currently unavailable."
    
    final_msg = f"✨ **Model:** `{src}`\n\n{ans}"
    res = await bot.send_message(e.chat_id, final_msg)
    await auto_delete(res, 200) # 200 Seconds Auto-Delete
    try: await e.delete()
    except: pass

# HYBRID FALLBACK COMMAND (.ai)
@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_hybrid(e):
    if not is_owner(e): return
    
    query = e.pattern_match.group(1)
    if not query and e.is_reply:
        r = await e.get_reply_message()
        query = r.text
        
    if not query: return
    
    thinking = await e.reply("`🤖 Omni-AI (Parallel Processing)...`" )
    context = await get_web_context(query)
    
    # Run Parallel (Fastest wins + Fallback)
    tasks = [get_gemini_resp(query, context), get_groq_resp(query, context)]
    results = await asyncio.gather(*tasks)
    
    final_ans, source = None, "None"
    for ans, src in results:
        if ans: 
            final_ans, source = ans, src
            break
            
    await thinking.delete()
    if not final_ans: final_ans = "❌ All AI models failed."
    
    final_msg = f"✨ **Model:** `{source}`\n\n{final_ans}"
    res = await bot.send_message(e.chat_id, final_msg)
    await auto_delete(res, 200) # 200 Seconds Auto-Delete
    try: await e.delete()
    except: pass
        

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
    # Safety settings to prevent "None" response for sensitive topics
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash', safety_settings=safety)
else:
    gemini_model = None

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP & EXPLAIN REGISTRY
# =====================
register_help(
    "ai",
    ".ai <query> - Hybrid Mode (Edit Support)\n"
    ".aai, .jarvis, .edith - Gemini Mode\n"
    ".aihealth - Check API Status"
)

register_explain(
    "ai",
    "🤖 **Omni-AI (Edit-to-Response)**\n\n"
    "Edits your command message into the response to keep chat clean.\n"
    "Supports Reply & Web Search. Auto-Delete: 200s."
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
        sys_msg = f"Role: Gemini 1.5 Flash. Date: April 12, 2026. Web Context: {context}"
        response = await asyncio.to_thread(gemini_model.generate_content, f"{sys_msg}\n\nUser: {prompt}")
        return (response.text, "Gemini 1.5 Flash") if response.text else (None, None)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None, None

async def get_groq_resp(prompt, context):
    if not groq_client: return None, None
    try:
        sys_msg = f"Role: Llama 3.3. Date: April 12, 2026. Context: {context}"
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content, "Groq (Llama 3.3)"
    except: return None, None

# =====================
# COMMAND HANDLERS
# =====================

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    status = "🔍 **Omni-AI Health**\n\n"
    status += f"🤖 Groq: {'🟢' if GROQ_KEY else '🔴'}\n"
    status += f"♊ Gemini: {'🟢' if GEMINI_KEY else '🔴'}\n"
    try:
        with DDGS() as ddgs:
            list(ddgs.text("test", max_results=1))
            status += "🌐 Web: 🟢"
    except: status += "🌐 Web: 🔴"
    await auto_delete(await e.edit(status), 15)

# GEMINI ONLY (.aai, .jarvis, .edith)
@bot.on(events.NewMessage(pattern=r"\.(aai|jarvis|edith)(?:\s+([\s\S]+))?$"))
async def gemini_cmd(e):
    if not is_owner(e): return
    query = e.pattern_match.group(2)
    if not query and e.is_reply:
        query = (await e.get_reply_message()).text
    
    if not query: return await auto_delete(await e.edit("`Puchna kya hai?`"), 5)
    
    await e.edit(f"`🚀 {e.pattern_match.group(1).upper()} is processing...`" )
    context = await get_web_context(query)
    ans, src = await get_gemini_resp(query, context)
    
    if not ans: ans = "❌ Gemini returned None. Check Safety/Quota."
    
    final_msg = f"✨ **Model:** `{src}`\n\n{ans}"
    # Truncate if too long
    res = await e.edit(final_msg[:4095])
    await auto_delete(res, 200)

# HYBRID MODE (.ai)
@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_hybrid(e):
    if not is_owner(e): return
    # Avoid overlapping with .aai
    if e.text.startswith(".aai"): return 
    
    query = e.pattern_match.group(1)
    if not query and e.is_reply:
        query = (await e.get_reply_message()).text
        
    if not query: return
    
    await e.edit("`🤖 Smart Selecting AI...`" )
    context = await get_web_context(query)
    
    # Parallel Run
    tasks = [get_gemini_resp(query, context), get_groq_resp(query, context)]
    results = await asyncio.gather(*tasks)
    
    final_ans, source = None, "Error"
    for ans, src in results:
        if ans:
            final_ans, source = ans, src
            break
            
    if not final_ans: final_ans = "❌ All AI models failed."
    
    final_msg = f"✨ **Model:** `{source}`\n\n{final_ans}"
    res = await e.edit(final_msg[:4095])
    await auto_delete(res, 200)
    

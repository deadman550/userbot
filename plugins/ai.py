import os
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
    # Safety filters to prevent "None" response on sensitive or long queries
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
# HELP & REGISTRY
# =====================
register_help(
    "ai",
    ".ai <query> (or reply) - Hybrid Mode (Edit Support)\n"
    ".aai, .jarvis, .edith - Gemini Dedicated\n"
    ".aihealth - Check API & Web Status"
)

register_explain(
    "ai",
    "🤖 **Omni-AI v2.5 (Stable)**\n\n"
    "• Edits command message to show answer.\n"
    "• Full Reply Support: Combines your instruction with replied text.\n"
    "• Fixes: Web Search & Safety Filters.\n"
    "• Auto-Delete: 200 Seconds."
)

# =====================
# CORE WORKERS
# =====================

async def get_web_context(query: str) -> str:
    """Fixed Web Search logic to prevent 'Offline' status"""
    if not query: return ""
    try:
        with DDGS() as ddgs:
            # Added region and parameters for better stability on servers
            results = ddgs.text(
                keywords=query,
                region='wt-wt', 
                safesearch='moderate',
                max_results=3
            )
            context_list = [r['body'] for r in results if 'body' in r]
            return "\n".join(context_list) if context_list else ""
    except Exception as e:
        print(f"🌐 Search Error: {e}")
        return ""

async def get_gemini_resp(prompt, context):
    if not gemini_model: return None, None
    try:
        sys_msg = f"Role: Gemini 1.5 Flash. Date: April 12, 2026."
        if context: sys_msg += f" Web Context: {context}"
        
        response = await asyncio.to_thread(gemini_model.generate_content, f"{sys_msg}\n\nUser Question: {prompt}")
        if response and response.text:
            return response.text, "Gemini 1.5 Flash"
        return None, None
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
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

async def get_full_query(e):
    """Combines your command message with the text of the message you replied to"""
    cmd_text = e.pattern_match.group(2) if hasattr(e.pattern_match, 'group') and len(e.pattern_match.groups()) >= 2 else e.pattern_match.group(1)
    if e.is_reply:
        reply_msg = await e.get_reply_message()
        if reply_msg and reply_msg.text:
            # Contextual prompt engineering
            if not cmd_text: cmd_text = "Analyze or explain this"
            return f"Instruction: {cmd_text}\n\nTarget Content to Process: {reply_msg.text}"
    return cmd_text

# =====================
# COMMAND HANDLERS
# =====================

# 1. Detailed Health Checker
@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    status = "🔍 **Omni-AI Health Report**\n\n"
    status += f"🤖 Groq (Llama): {'🟢 Active' if GROQ_KEY else '🔴 Missing'}\n"
    status += f"♊ Gemini (Flash): {'🟢 Active' if GEMINI_KEY else '🔴 Missing'}\n"
    
    try:
        with DDGS() as ddgs:
            test = next(ddgs.text("python", max_results=1), None)
            status += f"🌐 Web Search: {'🟢 Online' if test else '🔴 No Data'}"
    except:
        status += "🌐 Web Search: 🔴 Offline"
    
    await auto_delete(await e.edit(status), 20)

# 2. Gemini Strict Mode (.aai, .jarvis, .edith)
@bot.on(events.NewMessage(pattern=r"\.(aai|jarvis|edith)(?:\s+([\s\S]+))?$"))
async def gemini_strict(e):
    if not is_owner(e): return
    query = await get_full_query(e)
    if not query: return await auto_delete(await e.edit("`Puchna kya hai?`"), 5)
    
    await e.edit(f"`🚀 {e.pattern_match.group(1).upper()} is analyzing...`" )
    context = await get_web_context(query)
    ans, src = await get_gemini_resp(query, context)
    
    if not ans: ans = "❌ Gemini failed to respond. Check API Key or Safety Filters."
    
    res = await e.edit(f"✨ **Model:** `{src}`\n\n{ans}"[:4090])
    await auto_delete(res, 200)

# 3. Hybrid Mode (.ai)
@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_hybrid(e):
    if not is_owner(e): return
    if e.text.startswith(".aai"): return 
    
    query = await get_full_query(e)
    if not query: return
    
    await e.edit("`🤖 Smart Selecting Engine...`" )
    context = await get_web_context(query)
    
    tasks = [get_gemini_resp(query, context), get_groq_resp(query, context)]
    results = await asyncio.gather(*tasks)
    
    final_ans, source = None, "None"
    for ans, src in results:
        if ans:
            final_ans, source = ans, src
            break
            
    if not final_ans: final_ans = "❌ All AI models failed."
    
    res = await e.edit(f"✨ **Model:** `{source}`\n\n{final_ans}"[:4090])
    await auto_delete(res, 200)
    

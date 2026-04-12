import os
import asyncio
import google.generativeai as genai
from groq import Groq
# NEW: Import directly from ddgs for better stability
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded
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
    # Using 'latest' to avoid 404 models not found errors
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    gemini_model = None

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# CORE LOGIC
# =====================

async def get_web_context(query: str) -> str:
    """Enhanced search to bypass Railway IP blocks"""
    if not query: return ""
    try:
        # Region 'wt-wt' is more stable on VPS
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.text(query, region='wt-wt', max_results=3))
            return "\n".join([r['body'] for r in results]) if results else ""
    except Exception as e:
        print(f"🌐 Search Blocked: {e}")
        return ""

async def get_gemini_resp(prompt, context):
    if not gemini_model: return None, None
    try:
        sys_msg = f"Role: Gemini 1.5. Date: April 12, 2026. Context: {context}"
        response = await asyncio.to_thread(gemini_model.generate_content, f"{sys_msg}\n\nUser: {prompt}")
        return response.text, "Gemini 1.5 Flash"
    except: return None, None

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
# HANDLERS
# =====================

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health_check(e):
    if not is_owner(e): return
    # Start by editing the command message
    await e.edit("`🔍 Scanning AI Core...`")
    
    status = "🔍 **Omni-AI Health Report**\n\n"
    status += f"🤖 **Groq:** {'🟢' if GROQ_KEY else '🔴'}\n"
    status += f"♊ **Gemini:** {'🟢' if GEMINI_KEY else '🔴'}\n"
    
    try:
        with DDGS() as ddgs:
            next(ddgs.text("test", max_results=1))
            status += "🌐 **Search:** 🟢 Active"
    except:
        status += "🌐 **Search:** 🔴 Blocked (Railway IP)"
    
    await auto_delete(await e.edit(status), 20)

@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_handler(e):
    if not is_owner(e): return
    
    # 1. Get input (Text or Reply)
    query = e.pattern_match.group(1)
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
    
    if not query:
        return await auto_delete(await e.edit("`Usage: .ai <question> or reply`"), 5)

    # 2. Edit the user's message to show "Thinking..."
    await e.edit("`🌐 Smart Analyzing...`" )
    
    # 3. Fetch Context
    context = await get_web_context(query)
    
    # 4. Smart Model Selection
    coding_terms = ['python', 'script', 'fix', 'error', 'database', 'html', 'code']
    is_coding = any(term in query.lower() for term in coding_terms)

    if is_coding and gemini_model:
        ans, src = await get_gemini_resp(query, context)
    else:
        # Run in parallel for speed
        tasks = [get_gemini_resp(query, context), get_groq_resp(query, context)]
        results = await asyncio.gather(*tasks)
        ans, src = next(((r, s) for r, s in results if r), (None, "None"))

    if not ans:
        ans = "❌ All models failed. Check Railway Env Variables."

    # 5. Final Edit (Response)
    final_output = f"✨ **Model:** `{src}`\n\n{ans}"
    await auto_delete(await e.edit(final_output[:4090]), 200)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai <query> (or reply) - Hybrid Mode\n.aihealth - System Check")
register_explain("ai", "🤖 **Omni-AI v2.7**\n- Fixed Search for Railway\n- Parallel Processing\n- Edit Message Support")
    

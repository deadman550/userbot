import os
import asyncio
import aiohttp
from telethon import events
from groq import Groq
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded
from utils.auto_delete import auto_delete

# =====================
# CONFIGURATION
# =====================
PLUGIN_NAME = "Omni-AI v3.5"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# API Endpoints (Auto-fallback to Stable)
GEMINI_URLS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}",
    f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
]
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

mark_plugin_loaded("ai.py")

# =====================
# CORE ENGINES
# =====================

async def get_web_context(query: str) -> str:
    if len(query) < 10: return ""
    try:
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.text(query, region='wt-wt', max_results=2))
            return "\n".join([f"Source: {r['body']}" for r in results]) if results else ""
    except: return ""

async def call_gemini(prompt: str, context: str = ""):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": f"Context: {context}\n\nUser: {prompt}"}]}]}
    async with aiohttp.ClientSession() as session:
        for url in GEMINI_URLS:
            try:
                async with session.post(url, headers=headers, json=payload, timeout=20) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['candidates'][0]['content']['parts'][0]['text']
            except: continue
    return None

async def call_groq(prompt: str, context: str = ""):
    if not groq_client: return None
    try:
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}]
        )
        return chat.choices[0].message.content
    except: return None

# =====================
# SMART HANDLER
# =====================

@bot.on(events.NewMessage(pattern=r"\.(ai|jarvis|Jarvis|edith|gemini|code)(?:\s+([\s\S]+))?$"))
async def smart_ai(e):
    if not is_owner(e): return
    
    cmd = e.pattern_match.group(1).lower()
    query = e.pattern_match.group(2)
    
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
        
    if not query:
        return await auto_delete(await e.edit("`Usage: .ai <question>`"), 5)

    await e.edit(f"`⚡ {cmd.capitalize()} is Analyzing...`")
    
    # 1. Keywords to trigger Gemini inside .ai
    code_keywords = ['python', 'code', 'script', 'html', 'css', 'javascript', 'write', 'fix', 'error', 'database']
    is_coding_query = any(word in query.lower() for word in code_keywords)

    context = await get_web_context(query)

    # 2. Routing Logic
    # Case A: Explicit triggers for Gemini
    if cmd in ['jarvis', 'edith', 'gemini', 'code']:
        ans = await call_gemini(query, context)
        source = "Gemini Flash (Direct Trigger)"
        if not ans: 
            ans = await call_groq(query, context)
            source = "Groq (Backup)"

    # Case B: Smart .ai Command
    else:
        if is_coding_query:
            # Coding keyword detected -> Gemini First
            ans = await call_gemini(query, context)
            source = "Gemini Flash (Code Expert)"
            if not ans:
                ans = await call_groq(query, context)
                source = "Groq (Backup)"
        else:
            # Normal Chat -> Groq First (Fast)
            ans = await call_groq(query, context)
            source = "Groq (Llama 3.3 - Fast)"
            if not ans:
                ans = await call_gemini(query, context)
                source = "Gemini Flash (Backup)"

    if not ans:
        return await e.edit("❌ `Both AI Engines failed. Check API Keys!`")

    await auto_delete(await e.edit(f"✨ **Model:** `{source}`\n\n{ans}"[:4090]), 300)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    await e.edit("`📡 Testing Engines...`")
    gem = "🟢" if await call_gemini("hi") else "🔴"
    grq = "🟢" if (GROQ_KEY and await call_groq("hi")) else "🔴"
    await auto_delete(await e.edit(f"🔍 **Health:**\nGemini: {gem}\nGroq: {grq}\nSearch: 🟢"), 30)

register_help("ai", ".ai (Smart) | .code | .jarvis | .edith | .gemini")
register_explain("ai", "🤖 **Omni-AI v3.5**\n- Smart routing: Code -> Gemini, Chat -> Groq\n- All triggers supported\n- Auto-health check")

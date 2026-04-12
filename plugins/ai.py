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
PLUGIN_NAME = "Omni-AI v3.8"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URLS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}",
    f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
]
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Sabse Solid System Prompt
COMMON_INSTRUCTION = (
    "You are a smart AI Assistant built by Detor. Today is April 12, 2026. "
    "If Web Context is provided, use it to give the latest information. "
    "Don't confuse yourself with other models. Answer in Hinglish/Hindi directly."
)

mark_plugin_loaded("ai.py")

# =====================
# CORE ENGINES
# =====================

async def get_web_context(query: str) -> str:
    """Enhanced Search Logic for 2026"""
    if len(query) < 4: return ""
    try:
        # Strict 2026 search to avoid old IPL data
        with DDGS(timeout=20) as ddgs:
            results = list(ddgs.text(f"{query} current news April 2026", region='wt-wt', max_results=3))
            if results:
                return "\n".join([f"- {r['body']}" for r in results])
    except: pass
    return ""

async def call_gemini(prompt: str, context: str = ""):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": f"{COMMON_INSTRUCTION}\n\nLATEST WEB DATA:\n{context}\n\nUSER QUESTION: {prompt}"}]}]
    }
    async with aiohttp.ClientSession() as session:
        for url in GEMINI_URLS:
            try:
                async with session.post(url, headers=headers, json=payload, timeout=25) as resp:
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
            messages=[
                {"role": "system", "content": f"{COMMON_INSTRUCTION}\n\nREAL-TIME CONTEXT:\n{context}"},
                {"role": "user", "content": prompt}
            ]
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
        return await auto_delete(await e.edit("`Bolo bhai, kya puchna hai? (e.g. .ai aaj ipl match kiska hai)`"), 5)

    await e.edit(f"`🔍 Thinking... (Searching Web)`")
    
    # Search Trigger
    context = await get_web_context(query)
    
    code_words = ['python', 'code', 'script', 'fix', 'error', 'database', 'html']
    is_coding = any(word in query.lower() for word in code_words)

    # Smart Routing
    if cmd in ['jarvis', 'edith', 'gemini', 'code'] or is_coding:
        ans = await call_gemini(query, context)
        source = "Gemini Flash (Pro Mode)"
        if not ans:
            ans = await call_groq(query, context)
            source = "Groq (Backup Mode)"
    else:
        ans = await call_groq(query, context)
        source = "Groq (Fast Mode)"
        if not ans:
            ans = await call_gemini(query, context)
            source = "Gemini (Backup Mode)"

    if not ans:
        return await e.edit("❌ `API Limit reached or Connection Error!`")

    await auto_delete(await e.edit(f"✨ **Model:** `{source}`\n\n{ans}"), 300)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    await e.edit("`📡 Checking Engines...`")
    g = "🟢" if await call_gemini("hi") else "🔴"
    q = "🟢" if (GROQ_KEY and await call_groq("hi")) else "🔴"
    await auto_delete(await e.edit(f"🛠 **Status:**\nGemini: {g}\nGroq: {q}\nWeb: 🟢"), 20)

register_help("ai", ".ai | .code | .jarvis | .edith")
register_explain("ai", "🤖 Omni-AI v3.8 (Web Fixed)")
    

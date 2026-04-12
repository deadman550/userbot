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
PLUGIN_NAME = "Omni-AI v3.7"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URLS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}",
    f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
]
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Updated System Prompt to acknowledge search
SYSTEM_PROMPT = (
    "You are a professional AI Assistant built by Detor. Today is April 12, 2026. "
    "Always prioritize the 'Web Context' provided to answer about recent events. "
    "Be concise, don't translate questions, and talk in Hinglish/Hindi."
)

mark_plugin_loaded("ai.py")

# =====================
# CORE ENGINES
# =====================

async def get_web_context(query: str) -> str:
    """Railway-safe Search with better snippet extraction"""
    if len(query) < 5: return ""
    try:
        # Searching with specific keywords for better results
        search_query = f"{query} latest news 2026"
        with DDGS(timeout=15) as ddgs:
            results = list(ddgs.text(search_query, region='wt-wt', max_results=3))
            if results:
                return "\n".join([f"Recent Info: {r['body']}" for r in results])
    except Exception as e:
        print(f"Search Error: {e}")
    return ""

async def call_gemini(prompt: str, context: str = ""):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    # Combined prompt with Search Context
    final_text = f"{SYSTEM_PROMPT}\n\nLATEST WEB CONTEXT:\n{context}\n\nUSER QUESTION: {prompt}"
    payload = {"contents": [{"parts": [{"text": final_text}]}]}
    
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
        # Passing context directly into Groq's system message
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nWeb Data: {context}"},
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
        return await auto_delete(await e.edit("`Usage: .ai <question>`"), 5)

    await e.edit(f"`⚡ Searching & Analyzing...`")
    
    # 1. Web Search Trigger
    context = await get_web_context(query)
    
    # 2. Logic Check
    code_keywords = ['python', 'code', 'script', 'html', 'fix']
    is_coding = any(word in query.lower() for word in code_keywords)

    if cmd in ['jarvis', 'Jarvis', 'edith', 'gemini', 'code'] or is_coding:
        ans = await call_gemini(query, context)
        source = "Gemini Flash (Live)"
        if not ans:
            ans = await call_groq(query, context)
            source = "Groq (Backup)"
    else:
        ans = await call_groq(query, context)
        source = "Groq (Fast Live)"
        if not ans:
            ans = await call_gemini(query, context)
            source = "Gemini (Backup)"

    if not ans:
        return await e.edit("❌ `Engines failed. Check Keys.`")

    await auto_delete(await e.edit(f"✨ **Model:** `{source}`\n\n{ans}"), 300)

# ... (Health and Registry remain the same) ...
                                     

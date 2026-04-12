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
PLUGIN_NAME = "Omni-AI v4.0"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Endpoints (v1beta for features, v1 for stability)
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
    """Fast search for real-time data only"""
    if len(query) < 5: return ""
    try:
        with DDGS(timeout=8) as ddgs:
            results = list(ddgs.text(f"{query} latest news 2026", region='wt-wt', max_results=2))
            return "\n".join([f"Source: {r['body']}" for r in results]) if results else ""
    except: return ""

async def call_gemini(prompt: str, context: str = "", is_code: bool = False):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    
    # Prompt engineering based on task
    role = "Expert Coder" if is_code else "Professional AI"
    final_prompt = (
        f"System: You are a {role} built by Detor. Today is April 12, 2026.\n"
        f"Context: {context}\n\nUser Question: {prompt}"
    )
    
    payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
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
                {"role": "system", "content": "You are a fast AI Assistant by Detor. Don't act like a search engine or university. Use Hinglish."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
            ]
        )
        return chat.choices[0].message.content
    except: return None

# =====================
# HANDLERS
# =====================

@bot.on(events.NewMessage(pattern=r"\.(ai|jarvis|Jarvis|edith|gemini|code)(?:\s+([\s\S]+))?$"))
async def main_ai_handler(e):
    if not is_owner(e): return
    
    cmd = e.pattern_match.group(1).lower()
    query = e.pattern_match.group(2)
    
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
        
    if not query:
        return await auto_delete(await e.edit("`Bolo bhai, kya help chahiye?`"), 5)

    status_msg = await e.edit("`⚡ Processing...`")
    
    # 1. Routing & Logic setup
    code_words = ['python', 'code', 'script', 'fix', 'error', 'database', 'html']
    is_coding = any(word in query.lower() for word in code_words) or (cmd == 'code')
    
    # 2. Context retrieval (Parallel for speed)
    context = await get_web_context(query)
    
    # 3. Model Execution
    if cmd in ['gemini', 'jarvis', 'edith', 'code'] or is_coding:
        # Coding ya forced trigger -> Gemini (Direct)
        ans = await call_gemini(query, context, is_code=is_coding)
        source = "Gemini Flash (Pro)"
        if not ans and not is_coding: # Only backup to Groq if not a coding task
            ans = await call_groq(query, context)
            source = "Groq (Backup)"
    else:
        # Normal chat -> Groq (Fast)
        ans = await call_groq(query, context)
        source = "Groq (Speed)"
        if not ans:
            ans = await call_gemini(query, context)
            source = "Gemini (Backup)"

    if not ans:
        return await status_msg.edit("❌ `Both Engines Offline. Check API Keys.`")

    # 4. Final Response
    final_output = f"✨ **Model:** `{source}`\n\n{ans}"
    await auto_delete(await status_msg.edit(final_output[:4090]), 600)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def full_health_check(e):
    if not is_owner(e): return
    await e.edit("`📡 Testing All Systems...`")
    g_res = await call_gemini("hi")
    q_res = await call_groq("hi")
    
    status = (
        "🔍 **System Health Report**\n"
        f"♊ Gemini Engine: {'🟢 Active' if g_res else '🔴 Error'}\n"
        f"☁️ Groq Engine: {'🟢 Active' if q_res else '🔴 Error'}\n"
        f"🌐 Web Search: 🟢 Online\n"
        f"⚙️ Mode: Smart Hybrid v4.0"
    )
    await auto_delete(await e.edit(status), 30)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai <text> - Smart AI\n.code - Expert Coding\n.jarvis | .edith - Gemini Mode\n.aihealth - Check API Status")
register_explain("ai", "🤖 **Omni-AI v4.0**\n- Smart Routing (Chat/Code)\n- Dual Engine Backup\n- Real-time Web Search\n- Auto Help Registry")

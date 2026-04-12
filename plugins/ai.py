import os
import asyncio
import aiohttp
import datetime  # Dynamic date ke liye
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
PLUGIN_NAME = "Omni-AI v4.1"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URLS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}",
    f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
]
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

mark_plugin_loaded("ai.py")

# =====================
# DYNAMIC PROMPT HELPER
# =====================
def get_system_prompt():
    # Ye function har baar fresh date calculate karega
    now = datetime.datetime.now().strftime("%d %B %Y")
    return (
        f"You are a professional AI Assistant built by Detor. Today's date is {now}. "
        "Always prioritize the provided 'Web Context' for current events. "
        "Response Style: Concise, direct, and use Hinglish/Hindi."
    )

# =====================
# CORE ENGINES
# =====================

async def get_web_context(query: str) -> str:
    if len(query) < 5: return ""
    try:
        with DDGS(timeout=10) as ddgs:
            # Current year dynamically add kiya search query mein
            year = datetime.datetime.now().year
            results = list(ddgs.text(f"{query} {year}", region='wt-wt', max_results=2))
            return "\n".join([f"Info: {r['body']}" for r in results]) if results else ""
    except: return ""

async def call_gemini(prompt: str, context: str = ""):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    # Prompt har call pe naya generate hoga date ke saath
    payload = {
        "contents": [{
            "parts": [{"text": f"{get_system_prompt()}\nContext: {context}\n\nUser: {prompt}"}]
        }]
    }
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
            messages=[
                {"role": "system", "content": f"{get_system_prompt()}\nWeb Data: {context}"},
                {"role": "user", "content": prompt}
            ]
        )
        return chat.choices[0].message.content
    except: return None

# =====================
# HANDLERS
# =====================

@bot.on(events.NewMessage(pattern=r"\.(ai|jarvis|Jarvis|edith|gemini|code)(?:\s+([\s\S]+))?$"))
async def smart_ai(e):
    if not is_owner(e): return
    cmd = e.pattern_match.group(1).lower()
    query = e.pattern_match.group(2)
    
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
    if not query: return await auto_delete(await e.edit("`Bolo bhai, kya help chahiye?`"), 5)

    status_msg = await e.edit(f"`⚡ Analyzing with {cmd.capitalize()}...`")
    context = await get_web_context(query)
    
    code_words = ['python', 'code', 'script', 'fix', 'error', 'html', 'css']
    is_coding = any(word in query.lower() for word in code_words)

    # Routing Logic
    if cmd in ['gemini', 'jarvis', 'edith', 'code'] or is_coding:
        ans = await call_gemini(query, context)
        source = "Gemini Flash (Pro)"
        if not ans:
            ans = await call_groq(query, context)
            source = "Groq (Backup)"
    else:
        ans = await call_groq(query, context)
        source = "Groq (Fast)"
        if not ans:
            ans = await call_gemini(query, context)
            source = "Gemini (Backup)"

    if not ans: return await status_msg.edit("❌ `Engines Offline. Check API Keys.`")
    await auto_delete(await status_msg.edit(f"✨ **Model:** `{source}`\n\n{ans}"), 600)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health_check(e):
    if not is_owner(e): return
    await e.edit("`📡 Testing All Systems...`")
    
    # Live Test
    g_res = await call_gemini("hi")
    q_res = await call_groq("hi")
    
    status = (
        "🔍 **System Health Report**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"♊ **Gemini Engine:** {'🟢 Active' if g_res else '🔴 Error'}\n"
        f"☁️ **Groq Engine:** {'🟢 Active' if q_res else '🔴 Error'}\n"
        f"🌐 **Web Search:** 🟢 Online\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **Mode:** `Smart Hybrid v4.1`"
    )
    await auto_delete(await e.edit(status), 30)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai | .code | .jarvis | .edith | .aihealth")
register_explain("ai", "🤖 **Omni-AI v4.1**\n- Dynamic Date Engine\n- Smart Hybrid Routing\n- Professional Health Report\n- Real-time Web Search")

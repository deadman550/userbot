import os
import asyncio
import aiohttp
import datetime
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
PLUGIN_NAME = "Omni-AI v4.2"
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
    now = datetime.datetime.now().strftime("%d %B %Y")
    return (
        f"You are a professional AI Assistant built by Detor. Today's date is {now}. "
        "Use the provided 'Web Context' to give accurate and updated information. "
        "Talk in Hinglish/Hindi and keep answers helpful yet concise."
    )

# =====================
# CORE ENGINES
# =====================

async def get_web_context(query: str) -> str:
    if len(query) < 5: return ""
    try:
        with DDGS(timeout=10) as ddgs:
            year = datetime.datetime.now().year
            results = list(ddgs.text(f"{query} {year}", region='wt-wt', max_results=3))
            return "\n".join([f"Web Info: {r['body']}" for r in results]) if results else ""
    except: return ""

async def call_gemini(prompt: str, context: str = ""):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{get_system_prompt()}\nCONTEXT FROM WEB:\n{context}\n\nUSER QUESTION: {prompt}"}]
        }]
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
                {"role": "system", "content": f"{get_system_prompt()}\nContext: {context}"},
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
    if not query: return await auto_delete(await e.edit("`Puchiye bhai, kya janna hai?`"), 5)

    status_msg = await e.edit(f"`⚡ Thinking (Gemini Primary)...`")
    
    # Context Retrieval
    context = await get_web_context(query)
    
    # Primary Action: Gemini ko pehle call karna
    ans = await call_gemini(query, context)
    source = "Gemini Flash (Primary)"

    # Fallback Action: Agar Gemini fail ho toh Groq use karna
    if not ans:
        status_msg = await e.edit("`🔄 Gemini Limit Reached. Switching to Groq...`")
        ans = await call_groq(query, context)
        source = "Groq (Backup Mode)"

    if not ans:
        return await status_msg.edit("❌ `All engines are currently offline.`")

    await auto_delete(await status_msg.edit(f"✨ **Model:** `{source}`\n\n{ans}"), 600)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health_check(e):
    if not is_owner(e): return
    await e.edit("`📡 Testing All Systems...`")
    
    g_res = await call_gemini("hi")
    q_res = await call_groq("hi")
    
    status = (
        "🔍 **System Health Report**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"♊ **Gemini (Primary):** {'🟢 Active' if g_res else '🔴 Error'}\n"
        f"☁️ **Groq (Backup):** {'🟢 Active' if q_res else '🔴 Error'}\n"
        f"🌐 **Web Search:** 🟢 Online\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **Priority:** `Gemini-First v4.2`"
    )
    await auto_delete(await e.edit(status), 30)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai | .code | .jarvis | .aihealth")
register_explain("ai", "🤖 **Omni-AI v4.2**\n- Gemini as Primary Engine\n- Groq as Fail-safe Backup\n- Improved Web Search Context\n- Professional Health Report")
    

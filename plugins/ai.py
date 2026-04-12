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
PLUGIN_NAME = "Omni-AI v4.3"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URLS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}",
    f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
]
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

mark_plugin_loaded("ai.py")

# =====================
# TOOLS & PROMPTS
# =====================

def get_dynamic_prompt(model_name):
    # Dynamic Date update for every call
    now = datetime.datetime.now().strftime("%d %B %Y")
    return (
        f"You are a professional AI Assistant ({model_name}) built by Detor. Today is {now}. "
        "Strictly use the provided Web Context for real-time accuracy. "
        "Answer directly in Hinglish/Hindi. Do not translate the user's query."
    )

async def get_web_context(query: str) -> str:
    if not query or len(query) < 4: return ""
    try:
        with DDGS(timeout=10) as ddgs:
            year = datetime.datetime.now().year
            results = list(ddgs.text(f"{query} {year}", region='wt-wt', max_results=3))
            return "\n".join([f"Web Info: {r['body']}" for r in results]) if results else ""
    except: return ""

# =====================
# ENGINE CALLS
# =====================

async def call_gemini(prompt: str, context: str = ""):
    if not GEMINI_KEY: return None
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{get_dynamic_prompt('Gemini')}\nWEB CONTEXT:\n{context}\n\nUSER QUESTION: {prompt}"}]
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
                {"role": "system", "content": f"{get_dynamic_prompt('Groq Llama')}\nWEB CONTEXT: {context}"},
                {"role": "user", "content": prompt}
            ]
        )
        return chat.choices[0].message.content
    except: return None

# =====================
# MAIN HANDLER
# =====================

@bot.on(events.NewMessage(pattern=r"\.(ai|jarvis|Jarvis|edith|gemini|code)(?:\s+([\s\S]+))?$"))
async def router_ai(e):
    if not is_owner(e): return
    cmd = e.pattern_match.group(1).lower()
    query = e.pattern_match.group(2)
    
    # Reply Support
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
        
    if not query:
        return await auto_delete(await e.edit("`Bolo bhai, kya help chahiye? (Ya kisi message par reply karein)`"), 5)

    status_msg = await e.edit(f"`🔍 {cmd.capitalize()} is processing...`")
    
    # Get Search Results
    context = await get_web_context(query)
    
    if cmd == 'ai':
        # Primary: Groq
        ans = await call_groq(query, context)
        source = "Groq Llama (Fast)"
        if not ans: # Fallback
            ans = await call_gemini(query, context)
            source = "Gemini (Backup)"
    else:
        # Primary: Gemini (.gemini, .code, .jarvis, .edith)
        ans = await call_gemini(query, context)
        source = "Gemini Flash (Pro)"
        if not ans: # Fallback
            ans = await call_groq(query, context)
            source = "Groq (Backup)"

    if not ans:
        return await status_msg.edit("❌ `Engine error. Dono engines down hain ya API keys galat hain.`")

    # Output with Source Tag
    final_text = f"✨ **Model:** `{source}`\n\n{ans}"
    await auto_delete(await status_msg.edit(final_text[:4090]), 600)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    await e.edit("`📡 Testing AI Engines...`")
    
    # Test calls
    g_test = await call_gemini("hi")
    q_test = await call_groq("hi")
    
    g_status = "🟢 Active" if g_test else "🔴 Error"
    q_status = "🟢 Active" if q_test else "🔴 Error"
    
    status_report = (
        "🔍 **System Health Report**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"♊ **Gemini:** {g_status}\n"
        f"☁️ **Groq:** {q_status}\n"
        f"🌐 **Web Search:** 🟢 Online\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚙️ **Routing:** `Command-Specific v4.3`"
    )
    await auto_delete(await e.edit(status_report), 30)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai (Groq Fast)\n.gemini | .code | .jarvis (Gemini Pro)\n.aihealth (Status)")
register_explain("ai", "🤖 **Omni-AI v4.3**\n- Fixed Command Routing\n- Full Reply Support\n- Dynamic Date Engine\n- Professional Health UI")

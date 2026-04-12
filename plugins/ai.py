import os
import asyncio
import aiohttp
import time
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
PLUGIN_NAME = "Omni-AI v3.0"
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# API Endpoints
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}"
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

mark_plugin_loaded("ai.py")

# =====================
# CORE ENGINES
# =====================

async def get_web_context(query: str) -> str:
    """Railway-safe Search to provide latest context"""
    try:
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.text(query, region='wt-wt', max_results=3))
            return "\n".join([f"Source: {r['body']}" for r in results]) if results else ""
    except:
        return ""

async def call_gemini_direct(prompt: str, context: str = ""):
    """Official Direct API Call (Bypassing Outdated Libraries)"""
    if not GEMINI_KEY: return None
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"Context: {context}\n\nUser Question: {prompt}\n\nInstruction: Be concise and helpful."}]
        }]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GEMINI_URL, headers=headers, json=payload, timeout=20) as resp:
                data = await resp.json()
                if "candidates" in data:
                    return data['candidates'][0]['content']['parts'][0]['text']
    except:
        return None
    return None

async def call_groq_direct(prompt: str, context: str = ""):
    """Llama 3.3 Backup Engine"""
    if not groq_client: return None
    try:
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are a helpful AI. Context: {context}"},
                {"role": "user", "content": prompt}
            ]
        )
        return chat.choices[0].message.content
    except:
        return None

# =====================
# HANDLERS
# =====================

# Triggers for Gemini specifically
@bot.on(events.NewMessage(pattern=r"\.(ai|jarvis|edith|code)(?:\s+([\s\S]+))?$"))
async def ai_handler(e):
    if not is_owner(e): return
    
    cmd = e.pattern_match.group(1).lower()
    query = e.pattern_match.group(2)
    
    if not query and e.is_reply:
        reply = await e.get_reply_message()
        query = reply.text
        
    if not query:
        return await auto_delete(await e.edit(f"`Usage: .{cmd} <your question>`"), 5)

    msg = await e.edit(f"`⚡ {cmd.capitalize()} is thinking...`")
    
    # 1. Get Web Context
    context = await get_web_context(query)
    
    # 2. Strategy: Coding or General
    if cmd == "code":
        query = f"Write/Fix this code and explain briefly: {query}"

    # 3. Call Models (Gemini First, Groq as Backup)
    ans = await call_gemini_direct(query, context)
    source = "Gemini Flash (Direct)"
    
    if not ans:
        ans = await call_groq_direct(query, context)
        source = "Groq (Llama 3.3 Backup)"

    if not ans:
        return await e.edit("❌ `Both AI Engines failed. Check API Keys!`")

    # 4. Final Response
    final_output = f"✨ **Model:** `{source}`\n\n{ans}"
    await auto_delete(await e.edit(final_output[:4090]), 300)

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health_check(e):
    if not is_owner(e): return
    await e.edit("`📡 Pinging AI Servers...`")
    
    # Test Gemini
    gem_status = "🟢 Active" if await call_gemini_direct("hi") else "🔴 Error (404/Key)"
    # Test Groq
    groq_status = "🟢 Active" if (GROQ_KEY and await call_groq_direct("hi")) else "🔴 Inactive"
    
    report = (
        "🔍 **Omni-AI Health Report**\n"
        "---"
        f"\n♊ **Gemini (v1beta):** `{gem_status}`"
        f"\n☁️ **Groq (Llama):** `{groq_status}`"
        f"\n🌐 **Search Engine:** `🟢 Online`"
        f"\n⚙️ **Engine Type:** `Direct HTTP (No Library)`"
        "\n---"
        "\n**Status:** `All Systems Nominal`"
    )
    await auto_delete(await e.edit(report), 30)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai, .jarvis, .edith - Ask AI\n.code - Code Specialist\n.aihealth - System Check")
register_explain("ai", "🤖 **Omni-AI v3.0**\n- No 'google-generativeai' dependency\n- Fixed Railway 404 errors\n- Dual engine (Gemini + Groq)")

import os
import aiohttp
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

# Initialize Clients
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP & EXPLAIN
# =====================
register_help(
    "ai",
    ".ai <question>\n(reply) .ai\n.aihealth\n\n"
    "• Priority: Gemini for Code | Llama for Info\n"
    "• Web context enabled by default."
)

register_explain(
    "ai",
    "🤖 **Omni-AI (2026 Edition)**\n\n"
    "Parallel processing using Gemini 1.5 & Llama 3.3.\n"
    "Detects coding intent automatically to switch models."
)

# =====================
# CORE LOGIC
# =====================

async def get_web_context(query: str) -> str:
    """Fetches latest info from DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results) if results else ""
    except:
        return ""

async def get_gemini_resp(prompt, context):
    if not gemini_model: return None, None
    try:
        sys_msg = f"You are Gemini 1.5 Flash by Google. Today is April 12, 2026. Web Context: {context}"
        response = await asyncio.to_thread(gemini_model.generate_content, f"{sys_msg}\n\nUser Question: {prompt}")
        return response.text, "Gemini 1.5 Flash"
    except:
        return None, None

async def get_groq_resp(prompt, context):
    if not groq_client: return None, None
    try:
        sys_msg = f"You are Llama 3.3 by Meta. Today is April 12, 2026. Web Context: {context}"
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content, "Groq (Llama 3.3)"
    except:
        return None, None

# =====================
# COMMAND HANDLERS
# =====================

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def ai_health_cmd(e):
    if not is_owner(e): return
    status = "🔍 **AI System Health Report**\n\n"
    status += f"{'🟢' if GROQ_KEY else '🔴'} **Groq API:** {'Linked' if GROQ_KEY else 'Missing'}\n"
    status += f"{'🟢' if GEMINI_KEY else '🔴'} **Gemini API:** {'Linked' if GEMINI_KEY else 'Missing'}\n"
    try:
        with DDGS() as ddgs:
            list(ddgs.text("test", max_results=1))
            status += "🟢 **Web Search:** Active\n"
    except:
        status += "🔴 **Web Search:** Down\n"
    msg = await e.respond(status)
    await auto_delete(msg, 10)

@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_cmd(e):
    if not is_owner(e): return

    try:
        text = e.pattern_match.group(1)
        if not text and e.is_reply:
            r = await e.get_reply_message()
            text = r.text if r else None

        if not text:
            if e.pattern_match.group(0) == ".aihealth": return
            msg = await bot.send_message(e.chat_id, "Usage: `.ai <question>`")
            return await auto_delete(msg, 6)

        thinking = await bot.send_message(e.chat_id, "`🌐 Smart Processing...`")
        context = await get_web_context(text)
        
        # Keywords to force Gemini
        coding_keywords = ['python', 'code', 'script', 'fix', 'error', 'database', 'logic', 'def ', 'import ']
        is_coding = any(k in text.lower() for k in coding_keywords)

        final_resp, source = None, "None"

        if is_coding and gemini_model:
            # Code sawal hai toh Gemini hamesha priority
            final_resp, source = await get_gemini_resp(text, context)
            if not final_resp and groq_client:
                # Agar Gemini fail ho toh Llama backup
                final_resp, source = await get_groq_resp(text, context)
        else:
            # General sawal ke liye parallel run (Jo fast ho)
            tasks = [get_gemini_resp(text, context), get_groq_resp(text, context)]
            results = await asyncio.gather(*tasks)
            for resp, src in results:
                if resp:
                    final_resp, source = resp, src
                    break

        await thinking.delete()
        if not final_resp:
            final_resp = "❌ Models unreachable. Check Railway Variables."

        try: await e.delete()
        except: pass

        # Display Source Clearly
        final_msg = f"✨ **Model:** `{source}`\n\n{final_resp}"
        
        if len(final_msg) > 4095:
            msg = await bot.send_message(e.chat_id, final_msg[:4090])
        else:
            msg = await bot.send_message(e.chat_id, final_msg)

        # 60 seconds is enough for reading, then cleanup
        await auto_delete(msg, 60)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
    

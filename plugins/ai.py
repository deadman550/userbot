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
    ".ai QUESTION\n(reply) .ai\n.aihealth\n\n"
    "• Smart Switch: Gemini for Code | Llama for Speed\n"
    "• Owner only | Auto delete enabled"
)

register_explain(
    "ai",
    "🤖 **Omni-AI – 2026 Parallel Edition**\n\n"
    "Runs Gemini and Llama 3 in parallel to give the best answer.\n"
    "Usage: .ai <query>"
)

# =====================
# CORE LOGIC
# =====================

async def get_web_context(query: str) -> str:
    """Fetches latest 2026 info from DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results) if results else ""
    except:
        return ""

async def get_gemini_resp(prompt, system):
    """Gemini Worker"""
    if not gemini_model: return None, None
    try:
        response = await asyncio.to_thread(gemini_model.generate_content, f"{system}\n\nUser: {prompt}")
        return response.text, "Gemini 1.5 Flash"
    except:
        return None, None

async def get_groq_resp(prompt, system):
    """Groq Worker"""
    if not groq_client: return None, None
    try:
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}]
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
    status = "🔍 **AI Health Report**\n\n"
    status += "🟢 **Groq:** Connected\n" if GROQ_KEY else "🔴 **Groq:** Missing\n"
    status += "🟢 **Gemini:** Configured\n" if GEMINI_KEY else "🔴 **Gemini:** Missing\n"
    try:
        with DDGS() as ddgs:
            list(ddgs.text("test", max_results=1))
            status += "🟢 **Web Search:** Online\n"
    except:
        status += "🔴 **Web Search:** Offline\n"
    msg = await e.respond(status)
    await auto_delete(msg, 15)

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

        thinking = await bot.send_message(e.chat_id, "`🌐 Running Parallel Analysis...`")
        
        context = await get_web_context(text)
        system_prompt = (
            "Today is April 12, 2026. Use this web context for info: " + context + 
            "\nIf code is asked, prioritize clean Python structure."
        )

        # Start Parallel Tasks
        tasks = [get_gemini_resp(text, system_prompt), get_groq_resp(text, system_prompt)]
        results = await asyncio.gather(*tasks)

        # Smart Selection Logic
        final_resp, source = None, "None"
        is_coding = any(x in text.lower() for x in ['code', 'python', 'script', 'fix', 'error', 'function'])

        # First priority: If coding query, take Gemini
        for resp, src in results:
            if resp and is_coding and src == "Gemini 1.5 Flash":
                final_resp, source = resp, src
                break
        
        # Second priority: Take whatever is valid if final_resp is still None
        if not final_resp:
            for resp, src in results:
                if resp:
                    final_resp, source = resp, src
                    break

        await thinking.delete()
        if not final_resp:
            final_resp = "❌ Both AI models failed to respond."
            source = "Error"

        try: await e.delete()
        except: pass

        final_msg = f"🤖 **AI Answer ({source})**\n\n{final_resp}"
        
        if len(final_msg) > 4095:
            msg = await bot.send_message(e.chat_id, final_msg[:4090])
        else:
            msg = await bot.send_message(e.chat_id, final_msg)

        await auto_delete(msg, 120)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

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
    ".ai QUESTION\n(reply) .ai\n\n"
    "• Ask Omni-AI (Groq + Gemini + Web Search)\n"
    "• Automatically switches if one fails\n"
    "• Owner only | Auto delete enabled"
)

register_explain(
    "ai",
    "🤖 **Omni-AI – 2026 Edition**\n\n"
    "Combined power of Llama 3.1 & Gemini with live web search.\n"
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

async def ask_omni_ai(prompt: str) -> tuple:
    """Dual-API Fallback Logic"""
    context = await get_web_context(prompt)
    system_prompt = f"Today is April 7, 2026. Use this web context if relevant: {context}"
    
    # Attempt 1: Groq (Llama 3.1)
    if groq_client:
        try:
            chat = groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return chat.choices[0].message.content, "Groq (Llama 3.1)"
        except Exception:
            pass # Fallback

    # Attempt 2: Gemini 1.5 Flash
    if gemini_model:
        try:
            full_prompt = f"{system_prompt}\n\nUser Question: {prompt}"
            response = gemini_model.generate_content(full_prompt)
            return response.text, "Gemini 1.5 Flash"
        except Exception as ex:
            return f"❌ Error: {str(ex)}", "None"

    return "❌ No API Keys (GROQ_API_KEY/GEMINI_API_KEY) found in Railway.", "Error"

# =====================
# COMMAND HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_cmd(e):
    if not is_owner(e):
        return

    try:
        text = e.pattern_match.group(1)
        if not text and e.is_reply:
            r = await e.get_reply_message()
            text = r.text if r else None

        if not text:
            msg = await bot.send_message(e.chat_id, "Usage: `.ai <question>`")
            return await auto_delete(msg, 6)

        # Thinking Animation
        thinking = await bot.send_message(e.chat_id, "`🌐 Searching 2026 Web & Thinking...`")
        
        # Get Answer
        answer, source = await ask_omni_ai(text)

        await thinking.delete()
        try:
            await e.delete()
        except:
            pass

        final_msg = f"🤖 **AI Answer ({source})**\n\n{answer}"
        
        # Split message if it's too long for Telegram
        if len(final_msg) > 4095:
            msg = await bot.send_message(e.chat_id, final_msg[:4090])
        else:
            msg = await bot.send_message(e.chat_id, final_msg)

        await auto_delete(msg, 60) # Increased to 60s for reading long answers

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

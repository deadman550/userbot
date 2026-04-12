import os
import asyncio
import google.generativeai as genai
from groq import Groq
try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded
from utils.auto_delete import auto_delete

PLUGIN_NAME = "ai.py"

# =====================
# CONFIG & API SETUP
# =====================
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    # FIXED: 'gemini-1.5-flash-latest' prevents the 404 error found in logs
    gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest', safety_settings=safety)
else:
    gemini_model = None

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# CORE WORKERS
# =====================

async def get_web_context(query: str) -> str:
    """Fetches real-time web context for models"""
    if not query: return ""
    try:
        with DDGS() as ddgs:
            # Using list to ensure results are fetched before context closes
            results = list(ddgs.text(query, region='in-en', max_results=3))
            return "\n".join([r['body'] for r in results]) if results else ""
    except Exception as e:
        print(f"🌐 Search Error: {e}")
        return ""

async def get_gemini_resp(prompt, context):
    if not gemini_model: return None, None
    try:
        sys_msg = f"Role: Gemini Flash AI. Date: April 12, 2026. Web Context: {context}"
        response = await asyncio.to_thread(gemini_model.generate_content, f"{sys_msg}\n\nUser Question: {prompt}")
        if response and response.text:
            return response.text, "Gemini 1.5 Flash"
        return None, None
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        return None, None

async def get_groq_resp(prompt, context):
    if not groq_client: return None, None
    try:
        sys_msg = f"Role: Llama 3.3. Current Date: April 12, 2026. Context: {context}"
        chat = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content, "Groq (Llama 3.3)"
    except: return None, None

async def get_full_query(e):
    """Reads both command text and replied message text"""
    cmd_text = e.pattern_match.group(2) if hasattr(e.pattern_match, 'group') and len(e.pattern_match.groups()) >= 2 else e.pattern_match.group(1)
    if e.is_reply:
        reply_msg = await e.get_reply_message()
        if reply_msg and reply_msg.text:
            # Smart context building
            instruction = cmd_text or "Explain/Process this content"
            return f"Instruction: {instruction}\n\nTarget Content: {reply_msg.text}"
    return cmd_text

# =====================
# HANDLERS
# =====================

@bot.on(events.NewMessage(pattern=r"\.aihealth$"))
async def health(e):
    if not is_owner(e): return
    status = "🔍 **Omni-AI Health Report**\n\n"
    status += f"🤖 Groq: {'🟢' if GROQ_KEY else '🔴'}\n"
    status += f"♊ Gemini: {'🟢' if GEMINI_KEY else '🔴'}\n"
    try:
        with DDGS() as ddgs:
            test = next(ddgs.text("test", max_results=1), None)
            status += f"🌐 Search: {'🟢 Online' if test else '🔴 No Data'}"
    except: status += "🌐 Search: 🔴 Offline"
    await auto_delete(await e.edit(status), 20)

@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_main(e):
    if not is_owner(e): return
    if e.text.startswith(".aai"): return 
    
    query = await get_full_query(e)
    if not query: return
    
    # EDIT: Initial state to show activity
    await e.edit("`🤖 Analysing with Hybrid AI...`" )
    context = await get_web_context(query)
    
    # Parallel processing: First responder wins
    tasks = [get_gemini_resp(query, context), get_groq_resp(query, context)]
    results = await asyncio.gather(*tasks)
    
    final_ans, source = None, "Error"
    for ans, src in results:
        if ans:
            final_ans, source = ans, src
            break
            
    if not final_ans: final_ans = "❌ All AI models failed. Check Railway Logs."
    
    # EDIT: Replace processing text with final answer
    await auto_delete(await e.edit(f"✨ **Model:** `{source}`\n\n{final_ans}"[:4090]), 200)

# =====================
# REGISTRY
# =====================
register_help("ai", ".ai <query> (or reply) - Hybrid AI (Parallel)")
register_explain("ai", "🤖 **Omni-AI v2.6**\n\nParallel execution of Gemini and Llama with Web Search support.")

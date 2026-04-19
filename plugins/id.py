# plugins/id.py
import asyncio
from telethon import events
from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ id.py loaded")

register_help(
    "info",
    ".id\n"
    "Get detailed ID info of yourself, the chat, and replied users."
)

@bot.on(events.NewMessage(pattern=r"\.id(?:\s+.*)?$"))
async def get_id(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        # MERA DATA (Dynamic Name)
        me = await e.get_sender()
        my_name = me.first_name if me else "Owner"
        
        text = "<b>✨ ID INFORMATION</b>\n"
        text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        text += f"<b>👨‍💻 {my_name} ID:</b> <code>{e.sender_id}</code>\n"


        # 2. CHAT / GROUP DATA
        chat = await e.get_chat()
        if e.is_private:
            # Agar private chat hai toh dusre user ka naam dikhayega
            user_name = chat.first_name if hasattr(chat, 'first_name') else "User"
            text += f"<b>👤 User:</b> {user_name}\n"
            text += f"<b>🆔 User ID:</b> <code>{e.chat_id}</code>\n"
        else:
            # Agar group hai toh group ka naam
            text += f"<b>💬 Group:</b> {chat.title}\n"
            text += f"<b>🆔 Group ID:</b> <code>{e.chat_id}</code>\n"

        # 3. REPLIED USER DATA
        if e.is_reply:
            text += "\n<b>↩️ REPLIED TO:</b>\n"
            reply = await e.get_reply_message()
            
            if reply.sender_id:
                r_user = await reply.get_sender()
                r_name = r_user.first_name if r_user else "User"
                r_username = f"@{r_user.username}" if r_user and r_user.username else "No Username"
                
                text += f"<b>├ Name:</b> {r_name}\n"
                text += f"<b>├ ID:</b> <code>{reply.sender_id}</code>\n"
                text += f"<b>├ User:</b> {r_username}\n"
                # Permanent Link using user_id
                text += f"<b>└ Profile:</b> <a href='tg://openmessage?user_id={reply.sender_id}'>Permanent Link</a>\n"
            
            elif reply.sender_chat:
                text += f"<b>├ Channel:</b> {reply.sender_chat.title}\n"
                text += f"<b>└ ID:</b> <code>{reply.sender_chat.id}</code>\n"

        msg = await bot.send_message(
            e.chat_id, 
            text, 
            parse_mode='html',
            link_preview=False
        )

        await asyncio.sleep(20)
        await msg.delete()

    except Exception as ex:
        await log_error(bot, "id.py", ex)
        

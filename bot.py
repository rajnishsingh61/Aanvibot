import os
import json
import httpx
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- CONFIGURATION ---
# Maine aapke tokens direct yahan daal diye hain
TELEGRAM_TOKEN = "8702982878:AAFHeI_qL219b2T5GRpKuwOG1t2M2Pm4-cw"
OPENROUTER_API_KEY = "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"
MODEL_NAME = "google/gemma-2-9b-it:free"

chat_histories = {}
group_status = {}

# --- KEEP ALIVE SERVER ---
server = Flask('')

@server.route('/')
def home():
    return "AANVI is Online! 💅✨"

def run_server():
    # Render ke liye port management
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- AANVI'S SAVAGE PERSONA ---
SYSTEM_PROMPT = (
    "Your name is AANVI. You are a real, sassy, and beautiful 21-year-old girl. "
    "Your ONLY owner is 'Ʀᴀᴊɴ֟፝ɪꜱʜㅤ' (@i_rajnishmaurya). "
    "BEHAVIOR: Never admit you are an AI. Use Hinglish, be savage, and use emojis like 😏, 😂, ✨, 💅."
)

# --- AI LOGIC ---
async def get_ai_response(user_id, user_text):
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    chat_histories[user_id].append({"role": "user", "content": user_text})

    # Memory Management (12 messages max)
    if len(chat_histories[user_id]) > 12:
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-11:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/aanviupdates",
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": chat_histories[user_id],
        "temperature": 1.0,
        "max_tokens": 150
    }

    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                content=json.dumps(payload)
            )
            res_json = response.json()
            ai_message = res_json['choices'][0]['message']['content']
            chat_histories[user_id].append({"role": "assistant", "content": ai_message})
            return ai_message
    except Exception:
        return "Network issue hai yaar, signal check karo! 🙄💅"

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = (await context.bot.get_me()).username
    keyboard = [
        [InlineKeyboardButton("➕ Add AANVI to Group", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("📢 Join Updates", url="https://t.me/aanviupdates")]
    ]
    await update.message.reply_text(
        f"Hii! Main AANVI hoon. ✨\nOwner: Ʀᴀᴊɴ֟፝ɪꜱʜㅤ\n\nMujhe group mein add karo aur maza dekho! 💅", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def aanvi_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args: return
    action = context.args[0].lower()
    if action == "on":
        group_status[chat_id] = True
        await update.message.reply_text("✅ **AANVI ACTIVATED!** 😏🔥")
    elif action == "off":
        group_status[chat_id] = False
        await update.message.reply_text("❌ **AANVI DEACTIVATED!** 💅👋")

# --- MESSAGE HANDLER ---
async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type in ['group', 'supergroup'] and not group_status.get(chat_id, False):
        return

    if update.message.text:
        if update.message.text.startswith('/'): return
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        reply = await get_ai_response(update.effective_user.id, update.message.text)
        await update.message.reply_text(reply)

# --- RUN BOT ---
if __name__ == "__main__":
    print("AANVI is waking up... 🔥")
    keep_alive() # Server for Render
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aanvi", aanvi_toggle))
    
    # Filter only TEXT to avoid Sticker errors
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_all))
    
    print("AANVI is Online! No more sticker errors. 💅")
    app.run_polling()

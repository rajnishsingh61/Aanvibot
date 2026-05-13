import os
import json
import httpx
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- CONFIGURATION (Apni details yahan bhariye) ---
TELEGRAM_TOKEN = "8702982878:AAFHeI_qL219b2T5GRpKuwOG1t2M2Pm4-cw"
OPENROUTER_API_KEY = "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"
MODEL_NAME = "google/gemma-2-9b-it:free" # Sabse stable free model

chat_histories = {}
group_status = {}

# --- AANVI'S SAVAGE PERSONA ---
SYSTEM_PROMPT = (
    "Your name is AANVI. You are a real, sassy, beautiful 21-year-old girl. "
    "Your ONLY owner is 'Ʀᴀᴊɴ֟፝ɪꜱʜㅤ' (@i_rajnishmaurya). "
    "Talk in Hinglish, be savage, and use emojis like 😏, 😂, ✨, 💅. "
    "Never admit you are an AI. If someone sends only emojis, respond with attitude."
)

# --- AI RESPONSE LOGIC ---
async def get_ai_response(user_id, user_text):
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    chat_histories[user_id].append({"role": "user", "content": user_text})

    # History limit (Memory manage karne ke liye)
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-9:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/aanviupdates",
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": chat_histories[user_id],
        "temperature": 0.9,
        "max_tokens": 150
    }

    try:
        # Httpx is faster and better for network issues
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                res_json = response.json()
                ai_message = res_json['choices'][0]['message']['content']
                chat_histories[user_id].append({"role": "assistant", "content": ai_message})
                return ai_message
            else:
                return "Arre yaar, server nakhre kar raha hai! 🙄💅"
                
    except Exception as e:
        print(f"Error: {e}")
        return "Network issues... Ʀᴀᴊɴ֟፝ɪꜱʜㅤ se bolo fix kare! 🙄💨"

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📢 Updates", url="https://t.me/aanviupdates")]]
    await update.message.reply_text(
        "Hii! Main AANVI hoon. ✨\nOwner: Ʀᴀᴊɴ֟፝ɪꜱʜㅤ\n\nKaise yaad kiya mujhe? 😏", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def aanvi_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Usage: `/aanvi on` or `/aanvi off` 🙄")
        return
    
    action = context.args[0].lower()
    if action == "on":
        group_status[chat_id] = True
        await update.message.reply_text("✅ AANVI ACTIVATED! 😏🔥")
    elif action == "off":
        group_status[chat_id] = False
        await update.message.reply_text("❌ AANVI DEACTIVATED! 💅👋")

# --- MESSAGE HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Group check
    if update.effective_chat.type in ['group', 'supergroup'] and not group_status.get(chat_id, False):
        return

    if update.message.text:
        if update.message.text.startswith('/'): return
        
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        reply = await get_ai_response(update.effective_user.id, update.message.text)
        await update.message.reply_text(reply)

# --- MAIN BLOCK ---
if __name__ == "__main__":
    print("AANVI is starting... 🔥")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aanvi", aanvi_toggle))
    
    # SIRF Text filters, no stickers to avoid errors
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("AANVI is Online! Let's go! 💋")
    app.run_polling()

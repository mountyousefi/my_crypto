# bot_webhook_fastapi.py
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from analysis import simple_analysis, plot_chart
from fastapi import FastAPI, Request
import asyncio

TOKEN = "TELEGRAM_BOT_TOKEN_تو_اینجا"

# اپلیکیشن تلگرام
app_telegram = ApplicationBuilder().token(TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    
    simple_result = simple_analysis(symbol)
    chart_file = plot_chart(symbol)
    
    await update.message.reply_text(simple_result)
    await update.message.reply_photo(open(chart_file, 'rb'))

# اضافه کردن هندلر
app_telegram.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# اپلیکیشن FastAPI
app_fastapi = FastAPI()

@app_fastapi.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, Bot(TOKEN))
    await app_telegram.update_queue.put(update)
    return {"ok": True}

# برای اجرای لوکال یا uvicorn
if __name__ == "__main__":
    import uvicorn
    # پورت هاست شما می‌تواند متفاوت باشد
    uvicorn.run(app_fastapi, host="0.0.0.0", port=8443)
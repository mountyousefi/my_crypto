# bot.py
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from analysis import simple_analysis, plot_chart
from fastapi import FastAPI, Request

TOKEN = "8393971789:AAGbNCPDyRfVhdd-ReFpP_VPWwVgR5OaDkI"

# اپلیکیشن تلگرام
app_telegram = ApplicationBuilder().token(TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol_input = update.message.text.strip().upper()

    try:
        simple_result = simple_analysis(symbol_input)
        chart_file = plot_chart(symbol_input)

        await update.message.reply_text(simple_result)

        # ارسال تصویر اگر موجود بود
        if chart_file:
            try:
                with open(chart_file, 'rb') as photo:
                    await update.message.reply_photo(photo)
            except Exception as e:
                await update.message.reply_text(f"خطا در ارسال تصویر: {e}")
        else:
            await update.message.reply_text("نمودار موجود نیست.")

    except Exception as e:
        await update.message.reply_text(f"خطا در تحلیل {symbol_input}: {e}")

# اضافه کردن هندلر
app_telegram.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# اپلیکیشن FastAPI
app_fastapi = FastAPI()

# اجرای اپلیکیشن تلگرام هنگام شروع
@app_fastapi.on_event("startup")
async def startup():
    await app_telegram.initialize()
    await app_telegram.start()
    print("Bot started and ready to receive messages.")

# توقف اپلیکیشن تلگرام هنگام خاموش شدن
@app_fastapi.on_event("shutdown")
async def shutdown():
    await app_telegram.stop()
    await app_telegram.shutdown()
    print("Bot stopped.")

# وبهوک تلگرام
@app_fastapi.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, Bot(TOKEN))
    await app_telegram.update_queue.put(update)
    return {"ok": True}

# اجرای لوکال (در Render نیازی به این بخش نیست)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_fastapi, host="0.0.0.0", port=8443)
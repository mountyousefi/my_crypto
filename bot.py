# bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from analysis import simple_analysis,plot_chart

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    
    # تحلیل ساده
    simple_result = simple_analysis(symbol)
    
    # نمودار
    chart_file = plot_chart(symbol)
    
    # ارسال به کاربر
    await update.message.reply_text(simple_result)
    await update.message.reply_photo(open(chart_file, 'rb'))

if __name__ == "__main__":
    TOKEN = "8393971789:AAGbNCPDyRfVhdd-ReFpP_VPWwVgR5OaDkI"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# ----------- تحلیل تکنیکال -----------
def get_crypto_analysis(symbol="BTC/USDT", timeframe="1h", limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df['RSI'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['Signal'] = macd['MACDs_12_26_9']
    df['EMA20'] = ta.ema(df['close'], length=20)

    last_row = df.iloc[-1]

    analysis_text = f"""
📊 تحلیل تکنیکال {symbol} ({timeframe})

💰 قیمت فعلی: {last_row['close']:.2f} USDT
📅 زمان: {last_row['timestamp']}

📈 RSI (14): {last_row['RSI']:.2f} → {"خرید بیش از حد" if last_row['RSI'] > 70 else "فروش بیش از حد" if last_row['RSI'] < 30 else "نرمال"}
📉 MACD: {last_row['MACD']:.2f}
📉 Signal: {last_row['Signal']:.2f}
📊 EMA20: {last_row['EMA20']:.2f}

⚠️ این تحلیل صرفاً جهت اطلاع است و توصیه سرمایه‌گذاری نیست.
"""
    return analysis_text

# ----------- دکمه‌ها و هندلرها -----------
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("BTC/USDT", callback_data='BTC/USDT')],
        [InlineKeyboardButton("ETH/USDT", callback_data='ETH/USDT')],
        [InlineKeyboardButton("BNB/USDT", callback_data='BNB/USDT')],
        [InlineKeyboardButton("SOL/USDT", callback_data='SOL/USDT')],
        [InlineKeyboardButton("ADA/USDT", callback_data='ADA/USDT')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("ارز مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

def button_callback(update, context):
    query = update.callback_query
    query.answer()
    symbol = query.data
    analysis = get_crypto_analysis(symbol)
    query.edit_message_text(text=analysis)

# ----------- راه‌اندازی ربات -----------
def main():
    TOKEN = "8393971789:AAGbNCPDyRfVhdd-ReFpP_VPWwVgR5OaDkI"  # اینو با توکن رباتت عوض کن
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
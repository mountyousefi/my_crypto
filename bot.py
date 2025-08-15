import logging
import asyncio
import ccxt
import pandas as pd
import numpy as np
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import talib
from datetime import datetime

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = '8393971789:AAGbNCPDyRfVhdd-ReFpP_VPWwVgR5OaDkI'
WEBHOOK_URL = 'https://my-crypto-bsci.onrender.com'
PORT = int(os.environ.get('PORT', 5000))

# Initialize Flask app for webhook
app = Flask(__name__)

# Initialize exchange (using Binance)
exchange = ccxt.binance({
    'apiKey': '',  # Not needed for public data
    'secret': '',
    'sandbox': False,
})

# Top 10 cryptocurrencies
CRYPTO_SYMBOLS = {
    'Bitcoin': 'BTC/USDT',
    'Ethereum': 'ETH/USDT', 
    'BNB': 'BNB/USDT',
    'XRP': 'XRP/USDT',
    'Solana': 'SOL/USDT',
    'Dogecoin': 'DOGE/USDT',
    'Cardano': 'ADA/USDT',
    'TRON': 'TRX/USDT',
    'Avalanche': 'AVAX/USDT',
    'Chainlink': 'LINK/USDT'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with crypto keyboard."""
    
    # Create inline keyboard with crypto options
    keyboard = []
    crypto_list = list(CRYPTO_SYMBOLS.keys())
    
    # Create 2 columns of buttons
    for i in range(0, len(crypto_list), 2):
        row = []
        row.append(InlineKeyboardButton(crypto_list[i], callback_data=crypto_list[i]))
        if i + 1 < len(crypto_list):
            row.append(InlineKeyboardButton(crypto_list[i + 1], callback_data=crypto_list[i + 1]))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to Moein Crypto Bot! 🚀\n\n"
        "Select a cryptocurrency to get technical analysis:",
        reply_markup=reply_markup
    )

def fetch_ohlcv_data(symbol: str, timeframe: str = '4h', limit: int = 100):
    """Fetch OHLCV data from exchange."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

def technical_analysis(df):
    """Perform technical analysis using TA-Lib."""
    try:
        # Convert to numpy arrays
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        # Technical indicators
        # RSI (14 periods)
        rsi = talib.RSI(close, timeperiod=14)[-1]
        
        # MACD
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_val = macd[-1]
        signal_val = macdsignal[-1]
        
        # Moving Averages
        sma_20 = talib.SMA(close, timeperiod=20)[-1]
        ema_20 = talib.EMA(close, timeperiod=20)[-1]
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
        bb_upper_val = bb_upper[-1]
        bb_lower_val = bb_lower[-1]
        
        # Stochastic
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
        stoch_k = slowk[-1]
        stoch_d = slowd[-1]
        
        # Current price
        current_price = close[-1]
        
        return {
            'current_price': current_price,
            'rsi': rsi,
            'macd': macd_val,
            'macd_signal': signal_val,
            'sma_20': sma_20,
            'ema_20': ema_20,
            'bb_upper': bb_upper_val,
            'bb_lower': bb_lower_val,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d
        }
    except Exception as e:
        logger.error(f"Technical analysis error: {e}")
        return None

def generate_signal(indicators, symbol):
    """Generate trading signal based on technical indicators."""
    try:
        signals = []
        signal_strength = 0
        
        # RSI Analysis
        if indicators['rsi'] < 30:
            signals.append("🟢 RSI shows OVERSOLD condition (Bullish)")
            signal_strength += 2
        elif indicators['rsi'] > 70:
            signals.append("🔴 RSI shows OVERBOUGHT condition (Bearish)")
            signal_strength -= 2
        else:
            signals.append(f"🟡 RSI: {indicators['rsi']:.1f} (Neutral)")
        
        # MACD Analysis
        if indicators['macd'] > indicators['macd_signal']:
            signals.append("🟢 MACD above signal line (Bullish)")
            signal_strength += 1
        else:
            signals.append("🔴 MACD below signal line (Bearish)")
            signal_strength -= 1
        
        # Price vs Moving Averages
        current_price = indicators['current_price']
        if current_price > indicators['ema_20']:
            signals.append("🟢 Price above EMA-20 (Bullish)")
            signal_strength += 1
        else:
            signals.append("🔴 Price below EMA-20 (Bearish)")
            signal_strength -= 1
        
        # Bollinger Bands
        if current_price > indicators['bb_upper']:
            signals.append("🔴 Price above upper Bollinger Band (Overbought)")
            signal_strength -= 1
        elif current_price < indicators['bb_lower']:
            signals.append("🟢 Price below lower Bollinger Band (Oversold)")
            signal_strength += 1
        else:
            signals.append("🟡 Price within Bollinger Bands (Normal)")
        
        # Stochastic
        if indicators['stoch_k'] < 20 and indicators['stoch_d'] < 20:
            signals.append("🟢 Stochastic in oversold zone (Bullish)")
            signal_strength += 1
        elif indicators['stoch_k'] > 80 and indicators['stoch_d'] > 80:
            signals.append("🔴 Stochastic in overbought zone (Bearish)")
            signal_strength -= 1
        
        # Overall Signal
        if signal_strength >= 3:
            overall_signal = "🚀 STRONG BUY"
        elif signal_strength >= 1:
            overall_signal = "📈 BUY"
        elif signal_strength <= -3:
            overall_signal = "💥 STRONG SELL"
        elif signal_strength <= -1:
            overall_signal = "📉 SELL"
        else:
            overall_signal = "⚪ HOLD/NEUTRAL"
        
        return signals, overall_signal, signal_strength
        
    except Exception as e:
        logger.error(f"Signal generation error: {e}")
        return [], "❓ ERROR", 0

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks for crypto selection."""
    query = update.callback_query
    await query.answer()
    
    crypto_name = query.data
    symbol = CRYPTO_SYMBOLS.get(crypto_name)
    
    if not symbol:
        await query.edit_message_text("❌ Invalid cryptocurrency selected!")
        return
    
    # Send "analyzing" message
    await query.edit_message_text(f"🔍 Analyzing {crypto_name}...\nPlease wait...")
    
    # Fetch data and analyze
    df = fetch_ohlcv_data(symbol, timeframe='4h', limit=100)
    
    if df is None or len(df) < 50:
        await query.edit_message_text(f"❌ Unable to fetch data for {crypto_name}")
        return
    
    # Perform technical analysis
    indicators = technical_analysis(df)
    
    if indicators is None:
        await query.edit_message_text(f"❌ Technical analysis failed for {crypto_name}")
        return
    
    # Generate signals
    signals, overall_signal, strength = generate_signal(indicators, symbol)
    
    # Format response
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    response = f"""
📊 **{crypto_name} Analysis Report**
🕐 {current_time}
💰 Current Price: ${indicators['current_price']:.4f}

**Overall Signal: {overall_signal}**
Signal Strength: {strength}/6

**Technical Indicators:**
• RSI (14): {indicators['rsi']:.1f}
• MACD: {indicators['macd']:.6f}
• EMA-20: ${indicators['ema_20']:.4f}
• SMA-20: ${indicators['sma_20']:.4f}
• Stochastic K: {indicators['stoch_k']:.1f}

**Analysis:**
"""
    
    for signal in signals:
        response += f"\n• {signal}"
    
    response += f"""

**Bollinger Bands:**
• Upper: ${indicators['bb_upper']:.4f}
• Lower: ${indicators['bb_lower']:.4f}

⚠️ *This is not financial advice. Always do your own research before trading.*
    """
    
    # Create back button
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Go back to main menu."""
    query = update.callback_query
    await query.answer()
    
    # Recreate main menu
    keyboard = []
    crypto_list = list(CRYPTO_SYMBOLS.keys())
    
    for i in range(0, len(crypto_list), 2):
        row = []
        row.append(InlineKeyboardButton(crypto_list[i], callback_data=crypto_list[i]))
        if i + 1 < len(crypto_list):
            row.append(InlineKeyboardButton(crypto_list[i + 1], callback_data=crypto_list[i + 1]))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Welcome to Moein Crypto Bot! 🚀\n\n"
        "Select a cryptocurrency to get technical analysis:",
        reply_markup=reply_markup
    )

# Webhook route
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook requests."""
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.create_task(application.process_update(update))
    return 'OK'

@app.route('/')
def index():
    return 'Moein Crypto Bot is running!'

def main():
    """Main function to set up the bot."""
    global application
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="back_to_menu"))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Set webhook
    application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
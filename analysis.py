# analysis.py
import yfinance as yf
import matplotlib.pyplot as plt

# فقط ارزهایی که داده قطعی دارند
VALID_SYMBOLS = ["BTC-USD", "ETH-USD", "BNB-USD"]

def format_symbol(symbol):
    if symbol not in VALID_SYMBOLS:
        return "BTC-USD"  # fallback به BTC
    return symbol

def simple_analysis(symbol):
    symbol = format_symbol(symbol)
    # داده 30 روزه روزانه
    data = yf.download(symbol, period="30d", interval="1d", progress=False)
    if data.empty:
        return f"داده برای {symbol} موجود نیست."
    
    close = data['Close']
    last_price = close.iloc[-1]
    prev_price = close.iloc[-2]

    ma_short = close.rolling(window=3).mean().iloc[-1]
    ma_long = close.rolling(window=7).mean().iloc[-1]

    trend = "صعودی 📈" if ma_short > ma_long else "نزولی 📉"
    change = ((last_price - prev_price)/prev_price)*100

    return f"تحلیل {symbol}:\nروند کوتاه‌مدت: {trend}\nتغییر آخرین روز: {change:.2f}%"

def plot_chart(symbol):
    symbol = format_symbol(symbol)
    data = yf.download(symbol, period="30d", interval="1d", progress=False)
    if data.empty:
        return None

    plt.figure(figsize=(10,5))
    plt.plot(data['Close'], label='Close Price')
    plt.title(f"قیمت {symbol} در ۳۰ روز اخیر")
    plt.xlabel("روز")
    plt.ylabel("قیمت")
    plt.legend()
    filename = f"{symbol}_chart.jpg"
    plt.savefig(filename)
    plt.close()
    return filename
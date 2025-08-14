# analysis.py
import yfinance as yf
import matplotlib.pyplot as plt

# تحلیل ساده MA
def simple_analysis(symbol):
    try:
        data = yf.download(symbol, period="7d", interval="1h")
        close = data['Close']
        ma_short = close.rolling(window=3).mean().iloc[-1]
        ma_long = close.rolling(window=7).mean().iloc[-1]

        last_price = close.iloc[-1]
        prev_price = close.iloc[-2]

        trend = "صعودی 📈" if ma_short > ma_long else "نزولی 📉"
        change = ((last_price - prev_price) / prev_price) * 100

        return f"روند کوتاه‌مدت {symbol}: {trend}\nتغییر آخرین ساعت: {change:.2f}%"
    except Exception as e:
        return f"خطا در دریافت داده‌ها برای {symbol}."

# رسم نمودار 24 ساعته
def plot_chart(symbol):
    data = yf.download(symbol, period="1d", interval="1h")
    plt.figure(figsize=(10,5))
    plt.plot(data['Close'], label='Close Price')
    plt.title(f"قیمت {symbol} در 24 ساعت اخیر")
    plt.xlabel("ساعت")
    plt.ylabel("قیمت")
    plt.legend()
    filename = f"{symbol}_chart.jpg"
    plt.savefig(filename)
    plt.close()
    return filename
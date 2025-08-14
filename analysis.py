# analysis.py
import yfinance as yf
import matplotlib.pyplot as plt

# تحلیل ساده MA
def simple_analysis(symbol):
    try:
        # اگر فرمت ارز کامل نیست، فرض بر USD
        if '-' not in symbol:
            symbol += '-USD'

        # دریافت داده 7 روز گذشته با بازه 1 ساعت
        data = yf.download(symbol, period="7d", interval="1h")
        close = data['Close']

        if close.empty:
            return f"داده‌ای برای {symbol} دریافت نشد."

        # طول پنجره MA بر اساس داده موجود
        ma_short_window = min(3, len(close))
        ma_long_window = min(7, len(close))

        ma_short = close.rolling(window=ma_short_window).mean().iloc[-1]
        ma_long = close.rolling(window=ma_long_window).mean().iloc[-1]

        last_price = close.iloc[-1]
        prev_price = close.iloc[-2] if len(close) > 1 else close.iloc[-1]

        trend = "صعودی 📈" if ma_short > ma_long else "نزولی 📉"
        change = ((last_price - prev_price) / prev_price) * 100

        return f"روند کوتاه‌مدت {symbol}: {trend}\nتغییر آخرین ساعت: {change:.2f}%"

    except Exception as e:
        return f"خطا در تحلیل {symbol}: {e}"


# رسم نمودار 24 ساعته
def plot_chart(symbol):
    try:
        if '-' not in symbol:
            symbol += '-USD'

        data = yf.download(symbol, period="1d", interval="1h")
        if data.empty:
            return None  # داده موجود نیست

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

    except Exception as e:
        print(f"خطا در رسم نمودار {symbol}: {e}")
        return None
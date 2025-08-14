# analysis.py
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# تحلیل ساده MA
def simple_analysis(symbol):
    try:
        # دریافت داده‌های 30 روز با تایم فریم 1 روز
        data = yf.download(symbol, period="30d", interval="1d")

        if data.empty:
            return f"❌ داده‌ای برای {symbol} پیدا نشد."

        close = data['Close']

        # محاسبه میانگین متحرک کوتاه و بلند
        ma_short = close.rolling(window=3).mean().iloc[-1]
        ma_long = close.rolling(window=7).mean().iloc[-1]

        # بررسی NaN بودن
        if pd.isna(ma_short) or pd.isna(ma_long):
            return f"❌ داده کافی برای محاسبه میانگین {symbol} وجود ندارد."

        last_price = close.iloc[-1]
        prev_price = close.iloc[-2]

        trend = "صعودی 📈" if float(ma_short) > float(ma_long) else "نزولی 📉"
        change = ((last_price - prev_price) / prev_price) * 100

        return f"روند کوتاه‌مدت {symbol}: {trend}\nتغییر آخرین روز: {change:.2f}%"

    except Exception as e:
        return f"خطا در تحلیل {symbol}: {e}"


# رسم نمودار 30 روزه
def plot_chart(symbol):
    try:
        data = yf.download(symbol, period="30d", interval="1d")

        if data.empty:
            return None

        plt.figure(figsize=(10,5))
        plt.plot(data['Close'], label='Close Price')
        plt.title(f"قیمت {symbol} در 30 روز اخیر")
        plt.xlabel("تاریخ")
        plt.ylabel("قیمت")
        plt.legend()
        filename = f"{symbol}_chart.jpg"
        plt.savefig(filename)
        plt.close()
        return filename

    except Exception as e:
        print(f"خطا در رسم نمودار {symbol}: {e}")
        return None
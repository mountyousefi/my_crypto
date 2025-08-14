# analysis.py
import yfinance as yf
import matplotlib.pyplot as plt
import requests

# تبدیل نماد ساده به فرمت یاهوفایننس
def format_symbol(symbol):
    if '-' not in symbol:
        return symbol + '-USD'
    return symbol

# دانلود داده از Yahoo Finance با fallback به CoinGecko
def get_data(symbol, period="14d", interval="1d"):
    symbol_formatted = format_symbol(symbol)
    try:
        data = yf.download(symbol_formatted, period=period, interval=interval)
        if not data.empty and 'Close' in data.columns:
            return data['Close']
    except:
        pass

    # fallback CoinGecko
    try:
        coin_id = symbol.lower()
        days = 14 if interval=="1d" else 1  # ساعتی فقط 1 روز
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": str(days)}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        prices = [p[1] for p in data['prices']]
        return prices if prices else None
    except:
        return None

# تحلیل کوتاه‌مدت و بلندمدت
def simple_analysis(symbol):
    # داده ساعتی 1 روزه
    close_hourly = get_data(symbol, period="1d", interval="1h")
    if close_hourly and len(close_hourly)>=2:
        # اگر pandas Series هست
        if hasattr(close_hourly, 'iloc'):
            last_price = close_hourly.iloc[-1]
            prev_price = close_hourly.iloc[-2]
            ma_short = close_hourly.rolling(window=min(3,len(close_hourly))).mean().iloc[-1]
            ma_long = close_hourly.rolling(window=min(7,len(close_hourly))).mean().iloc[-1]
        else:  # لیست CoinGecko
            last_price = close_hourly[-1]
            prev_price = close_hourly[-2]
            ma_short = sum(close_hourly[-3:])/min(3,len(close_hourly))
            ma_long = sum(close_hourly[-7:])/min(7,len(close_hourly))
        trend = "صعودی 📈" if ma_short > ma_long else "نزولی 📉"
        change = ((last_price - prev_price)/prev_price)*100
        result = f"تحلیل کوتاه‌مدت {symbol.upper()}: {trend}\nتغییر آخرین ساعت: {change:.2f}%"
    else:
        result = f"داده کوتاه‌مدت برای {symbol.upper()} موجود نیست."

    # داده روزانه 14 روزه برای نمودار
    close_daily = get_data(symbol, period="14d", interval="1d")
    if close_daily:
        result += "\nتحلیل روزانه ۱۴ روز اخیر آماده است."
    else:
        result += "\nداده روزانه موجود نیست."

    return result

# رسم نمودار با fallback
def plot_chart(symbol):
    filename = f"{symbol.upper()}_chart.jpg"

    # ابتدا داده ساعتی
    close_hourly = get_data(symbol, period="1d", interval="1h")
    if not close_hourly:
        # fallback روزانه
        close_hourly = get_data(symbol, period="14d", interval="1d")
    if not close_hourly:
        return None

    plt.figure(figsize=(10,5))
    if hasattr(close_hourly, 'iloc'):
        plt.plot(close_hourly, label='Close Price')
    else:
        plt.plot(close_hourly, label='Close Price')
    plt.title(f"قیمت {symbol.upper()}")
    plt.xlabel("زمان")
    plt.ylabel("قیمت")
    plt.legend()
    plt.savefig(filename)
    plt.close()
    return filename
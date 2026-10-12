
import os
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MARKETS = {
    "الذهب XAUUSD": "XAUUSD=X",
    "البيتكوين BTCUSD": "BTC-USD",
}

def get_candles(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "15m"}
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()["chart"]["result"]
    if not result:
        raise ValueError("لا توجد بيانات للسوق")
    data = result[0]["indicators"]["quote"][0]
    return [
        float(close)
        for close in data["close"]
        if close is not None
    ]

def analyze(prices):
    if len(prices) < 50:
        return "انتظار", "البيانات غير كافية"

    ema20 = sum(prices[-20:]) / 20
    ema50 = sum(prices[-50:]) / 50
    last = prices[-1]
    previous = prices[-2]

    support = min(prices[-20:])
    resistance = max(prices[-20:])

    if ema20 > ema50 and last > ema20 and last > previous:
        signal = "CALL 🟢"
    elif ema20 < ema50 and last < ema20 and last < previous:
        signal = "PUT 🔴"
    else:
        signal = "انتظار ⏳"

    details = (
        f"السعر: {last:.4f}\n"
        f"دعم تقريبي: {support:.4f}\n"
        f"مقاومة تقريبية: {resistance:.4f}\n"
        f"EMA20: {ema20:.4f}\n"
        f"EMA50: {ema50:.4f}"
    )
    return signal, details

def send_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("إعدادات البوت غير مكتملة")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": message},
        timeout=20,
    )
    response.raise_for_status()

def main():
    messages = [
        "📊 تحليل تجريبي للأسواق — فريم 15 دقيقة",
        "⚠️ إشارات تعليمية وليست توصية مالية.",
    ]

    for name, symbol in MARKETS.items():
        try:
            prices = get_candles(symbol)
            signal, details = analyze(prices)
            messages.append(f"\n{name}\nالإشارة: {signal}\n{details}")
        except Exception as error:
            messages.append(f"\n{name}\nتعذر جلب البيانات: {error}")

    messages.append(
        "\nوقت الفحص: "
        + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    )
    send_message("\n".join(messages))

if __name__ == "__main__":
    main()
  

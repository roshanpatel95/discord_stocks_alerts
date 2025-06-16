import yfinance as yf
import requests
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

STOCKS = [
    "NVDA", "TSLA", "SPY", "QQQ", "AAPL", "AMZN", "AMD", "MSFT", "META", "RDDT", "CRWV",
    "GOOGL", "AVGO", "BRK.B", "TSM", "LLY", "WMT", "JPM", "V", "ORCL", "NFLX", "MA", "XOM",
    "COST", "JNJ", "PG", "KO", "PLTR", "UNH", "BABA"
]

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1368660131297890435/xgdR_CvxiO5CqPV2seECpE53dTdWUFvdopdwpak4ZsrN-VxeXzj63p-NMNU5Z3IP25ky"

def analyze_stock(ticker):
    df = yf.download(ticker, period="30d", interval="1d", progress=False)
    if df.empty or len(df) < 26:
        return None

    df['ema50'] = EMAIndicator(df['Close'], window=50).ema_indicator()
    df['ema200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
    df['macd'] = MACD(df['Close']).macd_diff()
    df['rsi'] = RSIIndicator(df['Close']).rsi()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    trend = "Up" if latest['ema50'] > latest['ema200'] else "Down"
    macd_signal = "Bullish" if latest['macd'] > 0 and prev['macd'] <= 0 else "Bearish" if latest['macd'] < 0 and prev['macd'] >= 0 else "Neutral"
    rsi_signal = "Overbought" if latest['rsi'] > 70 else "Oversold" if latest['rsi'] < 30 else "Neutral"

    if trend == "Up" and macd_signal == "Bullish" and rsi_signal != "Overbought":
        verdict = "Buy Call"
        stars = "⭐️⭐️⭐️⭐️"
    elif trend == "Down" and macd_signal == "Bearish" and rsi_signal != "Oversold":
        verdict = "Buy Put"
        stars = "⭐️⭐️⭐️⭐️"
    else:
        verdict = "Wait"
        stars = "⭐️⭐️"

    return {
        "ticker": ticker,
        "trend": trend,
        "macd": macd_signal,
        "rsi": round(latest['rsi'], 2),
        "verdict": verdict,
        "stars": stars
    }

def send_discord_message(message):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")

def format_alert(result):
    return (
        f":bar_chart: Morning Report: ${result['ticker']}\n"
        f"Trend: {result['trend']} :chart_with_upwards_trend:\n"
        f"MACD: {result['macd']}\n"
        f"RSI: {result['rsi']}\n"
        f"Recommended: {result['verdict']}\n"
        f"{result['stars']}\n"
    )

def main():
    messages = []
    for ticker in STOCKS:
        result = analyze_stock(ticker)
        if result:
            messages.append(format_alert(result))

    for i in range(0, len(messages), 10):
        batch = messages[i:i+10]
        send_discord_message("\n".join(batch))

if __name__ == "__main__":
    main()

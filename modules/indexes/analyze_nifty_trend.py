import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from modules.indicators.indicators import apply_all_indicators
from modules.utils.telegram_sender import send_telegram_message


def fetch_nifty_data(period="2mo", interval="1d") -> pd.DataFrame:
    df = yf.download("^NSEI", period=period, interval=interval, progress=False)
    df.reset_index(inplace=True)
    df.rename(columns=str.lower, inplace=True)
    return df


def interpret_nifty_trend(df: pd.DataFrame) -> str:
    df = apply_all_indicators(df)

    latest = df.iloc[-1]

    signals = {
        "RSI": latest.get("rsi", 0) > 60,
        "MACD": latest.get("macd", 0) > latest.get("macd_signal", 0),
        "Supertrend": latest.get("supertrend_signal", "") == "buy",
        "ADX": latest.get("adx", 0) > 20 and latest.get("di_plus", 0) > latest.get("di_minus", 0)
    }

    bullish_count = sum(signals.values())

    # Determine overall trend
    if bullish_count >= 3:
        trend = "📈 Bullish"
    elif bullish_count == 2:
        trend = "📊 Neutral"
    else:
        trend = "📉 Bearish"

    # Compose message
    details = "\n".join([f"{k}: {'✅' if v else '❌'}" for k, v in signals.items()])
    message = (
        f"🧭 *NIFTY Trend Analysis ({datetime.now().strftime('%d-%b-%Y')})*\n"
        f"\n*Trend:* {trend} ({bullish_count}/4 signals positive)\n\n"
        f"*Signals:*\n{details}"
    )
    return message


def main():
    print("📈 Fetching NIFTY data...")
    df = fetch_nifty_data()
    message = interpret_nifty_trend(df)
    print("📬 Sending to Telegram...")
    send_telegram_message(message, parse_mode="Markdown")


if __name__ == "__main__":
    main()

import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_ohlcv(symbol, period="6mo", interval="1d"):
    print(f"[fetch_price_data] Fetching OHLCV for {symbol}")
    df = yf.download(symbol + ".NS", period=period, interval=interval, progress=False)
    df.reset_index(inplace=True)
    df["symbol"] = symbol
    df.columns = df.columns.str.lower()
    return df

def fetch_price_data(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    import yfinance as yf
    import pandas as pd

    try:
        yf_symbol = symbol + ".NS"
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            print(f"[fetch_price_data] Warning: No data returned for symbol '{symbol}'")
            return pd.DataFrame()

        df.reset_index(inplace=True)
        df.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        df["symbol"] = symbol
        df = df[["date", "symbol", "open", "high", "low", "close", "volume"]]
        df.dropna(inplace=True)

        # Now print debug info after df is ready
        print(f"[fetch_price_data] OHLCV sample for {symbol}:\n{df.head()}")

        return df

    except Exception as e:
        print(f"[fetch_price_data] Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

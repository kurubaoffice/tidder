import yfinance as yf
import pandas as pd
from nsepython import nse_eq  # Make sure: pip install nsepython
from datetime import datetime

def fetch_price_data(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    try:
        yf_symbol = symbol + ".NS"
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)

        if not df.empty:
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

            print(f"[fetch_price_data] ✅ Fetched from yfinance: {symbol}, rows: {len(df)}")
            return df

        else:
            print(f"[fetch_price_data] ⚠️ yfinance returned empty for {symbol}. Falling back to NSE...")

            nse_df = nse_eq(symbol)
            if nse_df.empty:
                print(f"[fetch_price_data] ❌ NSE data also empty for {symbol}")
                return pd.DataFrame()

            nse_df.reset_index(inplace=True)
            nse_df.rename(columns={
                'DATE': 'date',
                'CLOSE_PRICE': 'close',
                'OPEN_PRICE': 'open',
                'HIGH_PRICE': 'high',
                'LOW_PRICE': 'low',
                'TOTAL_TRADED_QUANTITY': 'volume'
            }, inplace=True)
            nse_df['date'] = pd.to_datetime(nse_df['date'], errors='coerce')
            nse_df["symbol"] = symbol
            nse_df.sort_values("date", inplace=True)

            final_df = nse_df[["date", "symbol", "open", "high", "low", "close", "volume"]]
            final_df.dropna(inplace=True)

            print(f"[fetch_price_data] ✅ Fetched from NSE: {symbol}, rows: {len(final_df)}")
            return final_df

    except Exception as e:
        print(f"[fetch_price_data] ❌ Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

from nsepython import nse_eq
import yfinance as yf
import pandas as pd
from datetime import datetime
print(f"[DEBUG] Using fetch_price_data from: {__file__}")

def fetch_price_data(symbol: str, period: str = "9mo", interval: str = "1d") -> pd.DataFrame:
    print(f"[DEBUG] Using fetch_price_data from: {__file__}")
    print(f"[fetch_price_data] Trying yfinance for {symbol}...")
    print(f"[DEBUG] Symbol type: {type(symbol)}, value: {symbol}")

    df = pd.DataFrame()  # Initialize here to avoid "df not defined" errors

    try:
        df = yf.download(symbol + ".NS", period=period, interval=interval, progress=False)

        if df.empty:
            raise ValueError("YFinance returned empty DataFrame")

        # Normalize column names
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip().lower() for col in df.columns]
        else:
            df.columns = [str(col).strip().lower() for col in df.columns]

        df.reset_index(inplace=True)

        # Rename known variants to standard
        rename_map = {}
        for col in df.columns:
            if "open" in col and "open" not in rename_map:
                rename_map[col] = "open"
            elif "high" in col and "high" not in rename_map:
                rename_map[col] = "high"
            elif "low" in col and "low" not in rename_map:
                rename_map[col] = "low"
            elif "close" in col and "close" not in rename_map:
                rename_map[col] = "close"
            elif "volume" in col and "volume" not in rename_map:
                rename_map[col] = "volume"
            elif "date" in col.lower() and "date" not in rename_map:
                rename_map[col] = "date"

        df.rename(columns=rename_map, inplace=True)

        # Final validation
        expected_cols = ["date", "open", "high", "low", "close", "volume"]
        if not all(col in df.columns for col in expected_cols):
            raise ValueError(f"[fetch_price_data] Missing expected columns: {expected_cols}. Found: {df.columns.tolist()}")

        df["symbol"] = symbol
        df = df[["date", "symbol", "open", "high", "low", "close", "volume"]]

        if len(df) >= 30:
            print(f"[fetch_price_data] ✅ YFinance OK: {symbol}, rows: {len(df)}")
            return df
        else:
            print(f"[fetch_price_data] ⚠️ YFinance returned too few rows ({len(df)}). Falling back...")

    except Exception as e:
        print(f"[fetch_price_data] ❌ YFinance error: {e}. Falling back...")

    # === Fallback to NSE Python ===
    try:
        print(f"[fetch_price_data] 🔁 Trying fallback with nsepython for {symbol}")
        raw_data = nse_eq(symbol)
        historical = raw_data["priceInfo"]["historical"]
        df = pd.DataFrame(historical)

        df["date"] = pd.to_datetime(df["date"])
        df.rename(columns={
            "open": "open",
            "dayHigh": "high",
            "dayLow": "low",
            "close": "close",
            "totalTradedVolume": "volume"
        }, inplace=True)
        df["symbol"] = symbol
        df = df[["date", "symbol", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("date")

        print(f"[fetch_price_data] ✅ Fallback NSE OK: {symbol}, rows: {len(df)}")
        return df
    except Exception as e:
        print(f"[fetch_price_data] ❌ NSE fallback also failed for {symbol}: {e}")

    return df  # Will return empty DataFrame if both failed




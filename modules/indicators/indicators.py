import pandas as pd
import os
import ta  # Make sure this is 'ta' package: pip install ta
import logging
from modules.data_fetcher.fetch_price_data import fetch_price_data
import os
import pandas as pd
import logging
from modules.data_fetcher.fetch_price_data import fetch_price_data
from modules.indicators.apply_indicators import apply_all_indicators

logger = logging.getLogger(__name__)


def apply_all_indicators(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    try:
        assert isinstance(df, pd.DataFrame), f"[apply_all_indicators] Expected DataFrame, got {type(df)}"

        # Flatten column names if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip().lower() for col in df.columns]
            print("[DEBUG] Flattened MultiIndex columns")
        else:
            df.columns = [str(col).strip().lower() for col in df.columns]

        print(f"[DEBUG] df BEFORE apply_all_indicators (type={type(df)}):")
        print(df.head(2))
        print("[DEBUG] dtypes:\n", df.dtypes)
        print("[DEBUG] Last 3 rows before indicators:\n", df.tail(3))
        print("[DEBUG] Config passed to apply_all_indicators:")
        for k, v in config.items():
            print(f"  {k}: {v} (type: {type(v)})")

        # 🔍 Identify 'close' column dynamically
        close_col = next((col for col in df.columns if col.startswith("close")), None)
        if not close_col:
            raise ValueError("No valid 'close' column found in DataFrame")
        print(f"[DEBUG] Using close column: {close_col}")

        # RSI
        if config.get("rsi", True):
            rsi_period = config.get("rsi_period", 14)
            if not isinstance(rsi_period, int):
                raise ValueError(f"rsi_period must be int, got {type(rsi_period)}")
            rsi = ta.momentum.RSIIndicator(close=df[close_col], window=rsi_period)
            df[f"rsi_{rsi_period}"] = rsi.rsi()
            print(f"[DEBUG] RSI applied with period: {rsi_period}")

        # MACD
        if config.get("macd", True):
            macd_fast = config.get("macd_fast", 12)
            macd_slow = config.get("macd_slow", 26)
            macd_signal = config.get("macd_signal", 9)
            if not all(isinstance(x, int) for x in [macd_fast, macd_slow, macd_signal]):
                raise ValueError("MACD params must be integers")
            macd = ta.trend.MACD(
                close=df[close_col],
                window_fast=macd_fast,
                window_slow=macd_slow,
                window_sign=macd_signal,
            )
            df["macd"] = macd.macd()
            df["macd_signal"] = macd.macd_signal()
            print(f"[DEBUG] MACD applied: fast={macd_fast}, slow={macd_slow}, signal={macd_signal}")

        # Bollinger Bands
        if config.get("bollinger_bands", True):
            bb_window = config.get("bb_window", 20)
            bb_std = config.get("bb_std", 2)
            if not isinstance(bb_window, int) or not isinstance(bb_std, (int, float)):
                raise ValueError("Bollinger Band params must be numeric")
            bb = ta.volatility.BollingerBands(
                close=df[close_col],
                window=bb_window,
                window_dev=bb_std,
            )
            df["bb_upper"] = bb.bollinger_hband()
            df["bb_lower"] = bb.bollinger_lband()
            print(f"[DEBUG] Bollinger Bands applied: window={bb_window}, std={bb_std}")

        # ✅ DEBUG after calculation
        print("[DEBUG] Columns after indicator application:", df.columns)
        print(df.tail(2))
        # ✅ DEBUG after calculation — safe checks
        for col in ["rsi_14", "macd", "macd_signal", "bb_upper", "bb_lower"]:
            if col in df.columns:
                print(f"[DEBUG] Non-null {col}: {df[col].notna().sum()}")
            else:
                print(f"[DEBUG] {col} not found in DataFrame")

        if f"rsi_{rsi_period}" in df.columns:
            print(f"[DEBUG] First 5 non-null RSI values:")
            print(df[df[f"rsi_{rsi_period}"].notnull()].head())
            print(f"[DEBUG] Total non-null RSI count:", df[f"rsi_{rsi_period}"].notnull().sum())

        return df

    except Exception as e:
        print(f"[apply_all_indicators] Failed to apply indicators: {e}")
        raise


def process_and_save_indicators(symbol: str, config: dict = None) -> str:
    config = config or {}

    try:
        df = fetch_price_data(symbol)
        print(f"[DEBUG] Type of df returned: {type(df)}")  # Add this line
        df = df[df["close"].notnull()]
        if df is None or df.empty:
            raise ValueError(f"[{symbol}] Price data fetch failed or returned empty")

        logger.info(f"[{symbol}] Processing indicators")
        df = apply_all_indicators(df, config)
        print(f"[DEBUG] Indicator DF head for {symbol}:\n", df.head(20))
        print(f"[DEBUG] Last row:\n{df.tail(1)}")

        # ✅ Fix path to project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        output_dir = os.path.join(project_root, "data", "processed")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "technical_indicators.csv")
        print(f"[DEBUG] Saving CSV to: {output_path}")
        df.to_csv(output_path, index=False)
        print(df.tail(2))

        return output_path

    except Exception as e:
        logger.error(f"[ERROR] Failed to process indicators for {symbol}: {e}")
        raise


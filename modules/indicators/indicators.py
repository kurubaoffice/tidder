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
        df.columns = [col.lower() for col in df.columns]

        if config.get("rsi", True):
            rsi_period = config.get("rsi_period", 14)
            rsi = ta.momentum.RSIIndicator(close=df["close"], window=rsi_period)
            df[f"rsi_{rsi_period}"] = rsi.rsi()

        if config.get("macd", True):
            macd_fast = config.get("macd_fast", 12)
            macd_slow = config.get("macd_slow", 26)
            macd_signal = config.get("macd_signal", 9)
            macd = ta.trend.MACD(
                close=df["close"],
                window_fast=macd_fast,
                window_slow=macd_slow,
                window_sign=macd_signal,
            )
            df["macd"] = macd.macd()
            df["macd_signal"] = macd.macd_signal()

        if config.get("bollinger_bands", True):
            bb_window = config.get("bb_window", 20)
            bb_std = config.get("bb_std", 2)
            bb = ta.volatility.BollingerBands(
                close=df["close"],
                window=bb_window,
                window_dev=bb_std,
            )
            df["bb_upper"] = bb.bollinger_hband()
            df["bb_lower"] = bb.bollinger_lband()

        # ✅ DEBUG: Now placed correctly
        print("[DEBUG] Columns after indicator application:", df.columns)
        print(df.tail(2))

        return df

    except Exception as e:
        logger.error(f"[apply_all_indicators] Failed to apply indicators: {e}")
        raise


def process_and_save_indicators(symbol: str, config: dict = None) -> str:
    config = config or {}

    try:
        df = fetch_price_data(symbol)
        if df is None or df.empty:
            raise ValueError(f"[{symbol}] Price data fetch failed or returned empty")

        logger.info(f"[{symbol}] Processing indicators")
        df = apply_all_indicators(df, config)

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


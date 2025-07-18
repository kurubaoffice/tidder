# modules/indicators/indicators.py

import pandas as pd
import time
from ta.trend import ADXIndicator
import ta
import os
import pandas as pd
from .ta_calculations import apply_all_indicators

from modules.data_fetcher.fetch_price_data import fetch_price_data # wherever your price fetch is


def process_and_save_indicators(symbol: str):
    try:
        # Step 1: Get live price OHLCV data
        df = fetch_price_data(symbol)
        if df is None or df.empty:
            print(f"Price data not found for {symbol}")
            return

        df['symbol'] = symbol

        # Step 2: Apply all indicators
        df_indicators = apply_all_indicators(df)

        # ➕ Drop rows with missing critical indicators (like RSI or MACD)
        df_indicators.dropna(subset=["rsi_14", "macd", "macd_signal"], inplace=True)

        # Step 3: Select only useful columns
        keep_cols = ['symbol'] + [col for col in df_indicators.columns if any(x in col.lower() for x in [
            'rsi', 'macd', 'signal', 'atr', 'bb_upper', 'bb_lower', 'adx', 'supertrend', 'stoch'
        ])]
        df_selected = df_indicators[keep_cols]

        # Round values and rename for clean output
        df_indicators = df_indicators.round({
            "rsi_14": 2,
            "macd": 2,
            "macd_signal": 2
        })

        df_indicators.rename(columns={
            "rsi_14": "RSI(14)",
            "macd": "MACD",
            "macd_signal": "MACD Signal"
        }, inplace=True)

        # Step 4: Save to CSV
        print("[DEBUG] DataFrame to save:")
        print(df_selected.head())
        output_path = os.path.join("data", "processed", "technical_indicators.csv")

        # If file exists, append or replace row
        if os.path.exists(output_path):
            existing = pd.read_csv(output_path)
            existing = existing[existing['symbol'] != symbol]  # Remove old row
            combined = pd.concat([existing, df_selected], ignore_index=True)
        else:
            combined = df_selected

        combined.to_csv(output_path, index=False)
        print(f" Indicators saved for {symbol} to {output_path}")
    except Exception as e:
        print(f" Failed to process indicators for {symbol}: {e}")
    if len(df) < 30:
        print(f"[WARN] Not enough data to compute indicators for {symbol} (rows: {len(df)})")

def prepare_dataframe_for_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and map necessary columns for indicator calculation.
    Ensures 'close', 'high', 'low', and 'volume' columns exist and are numeric.
    """
    df.columns = [col.lower() for col in df.columns]  # Normalize column names

    # Map 'close' column
    if 'close' not in df.columns:
        for fallback in ['regularmarketprice', 'currentprice', 'previousclose']:
            if fallback in df.columns:
                df['close'] = df[fallback]
                break

    # Map 'high' column
    if 'high' not in df.columns:
        for fallback in ['regularmarketdayhigh', 'dayhigh']:
            if fallback in df.columns:
                df['high'] = df[fallback]
                break

    # Map 'low' column
    if 'low' not in df.columns:
        for fallback in ['regularmarketdaylow', 'daylow']:
            if fallback in df.columns:
                df['low'] = df[fallback]
                break

    # Map 'volume' column
    if 'volume' not in df.columns:
        for fallback in ['regularmarketvolume', 'averagevolume']:
            if fallback in df.columns:
                df['volume'] = df[fallback]
                break

    # Convert relevant columns to numeric
    for col in ['close', 'high', 'low', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def apply_all_indicators(df: pd.DataFrame, indicators=None, config=None) -> pd.DataFrame:
    if indicators is None:
        indicators = ["rsi", "macd", "adx", "atr", "supertrend"]
    if config is None:
        config = {}

    df = prepare_dataframe_for_indicators(df)

    # RSI
    if 'rsi' in indicators and 'close' in df.columns:
        rsi_period = config.get("rsi_period", 14)
        if len(df) >= rsi_period:
            df[f"rsi_{rsi_period}"] = ta.momentum.RSIIndicator(close=df['close'], window=rsi_period).rsi()
        else:
            df[f"rsi_{rsi_period}"] = None

    # MACD
    if 'macd' in indicators and 'close' in df.columns:
        macd_fast = config.get("macd_fast", 12)
        macd_slow = config.get("macd_slow", 26)
        macd_signal = config.get("macd_signal", 9)
        min_len = max(macd_fast, macd_slow, macd_signal)
        if len(df) >= min_len:
            macd_obj = ta.trend.MACD(close=df['close'], window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_signal)
            df['macd'] = macd_obj.macd()
            df['macd_signal'] = macd_obj.macd_signal()
        else:
            df['macd'] = None
            df['macd_signal'] = None

    # ADX
    adx_indicator = ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14)
    df["adx"] = adx_indicator.adx()

    # ATR (14-period)
    df["tr"] = df[["high", "low", "close"]].copy().apply(
        lambda row: max(row["high"] - row["low"],
                        abs(row["high"] - row["close"]),
                        abs(row["low"] - row["close"])), axis=1
    )
    df["atr_14"] = df["tr"].rolling(window=14).mean()
    df.drop(columns=["tr"], inplace=True)

    # Supertrend
    if 'supertrend' in indicators and all(col in df.columns for col in ['high', 'low', 'close']):
        st_period = config.get("supertrend_period", 10)
        st_multiplier = config.get("supertrend_multiplier", 3.0)

        if len(df) >= st_period:
            atr = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=st_period)
            atr_values = atr.average_true_range()

            hl2 = (df['high'] + df['low']) / 2
            upperband = hl2 + (st_multiplier * atr_values)
            lowerband = hl2 - (st_multiplier * atr_values)

            supertrend = [True] * len(df)

            for i in range(1, len(df)):
                if df['close'].iloc[i] > upperband.iloc[i - 1]:
                    supertrend[i] = True
                elif df['close'].iloc[i] < lowerband.iloc[i - 1]:
                    supertrend[i] = False
                else:
                    supertrend[i] = supertrend[i - 1]
                    if supertrend[i] and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                        lowerband.iloc[i] = lowerband.iloc[i - 1]
                    if not supertrend[i] and upperband.iloc[i] > upperband.iloc[i - 1]:
                        upperband.iloc[i] = upperband.iloc[i - 1]

            df[f"supertrend_{st_period}_{st_multiplier}_dir"] = supertrend
            df[f"supertrend_{st_period}_{st_multiplier}_upper"] = upperband
            df[f"supertrend_{st_period}_{st_multiplier}_lower"] = lowerband
        else:
            df[f"supertrend_{st_period}_{st_multiplier}_dir"] = None
            df[f"supertrend_{st_period}_{st_multiplier}_upper"] = None
            df[f"supertrend_{st_period}_{st_multiplier}_lower"] = None


    # Bollinger Bands
    if ('bollinger' in indicators or 'bb' in indicators) and 'close' in df.columns:
        bb_window = config.get("bb_window", 20)
        bb_std = config.get("bb_std", 2)
        if len(df) >= bb_window:
            bb = ta.volatility.BollingerBands(close=df['close'], window=bb_window, window_dev=bb_std)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
        else:
            df['bb_upper'] = None
            df['bb_lower'] = None

    # Stochastic Oscillator
    if 'stochastic' in indicators and all(col in df.columns for col in ['high', 'low', 'close']):
        stoch_k = config.get("stoch_k", 14)
        stoch_d = config.get("stoch_d", 3)
        if len(df) >= stoch_k:
            stoch = ta.momentum.StochasticOscillator(high=df['high'], low=df['low'], close=df['close'],
                                                      window=stoch_k, smooth_window=stoch_d)
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
        else:
            df['stoch_k'] = None
            df['stoch_d'] = None

    return df

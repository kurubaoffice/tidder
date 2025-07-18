import pandas as pd
import numpy as np
import ta


def apply_all_indicators(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    Apply multiple technical indicators (RSI, MACD, Bollinger Bands, etc.)
    Args:
        df (pd.DataFrame): Input dataframe with 'close', 'high', 'low', 'volume'
        config (dict): Optional config for indicator parameters
    Returns:
        pd.DataFrame: DataFrame with indicator columns added
    """

    # Basic defaults if not provided
    config = config or {
        "rsi_period": 14,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "adx_period": 14,
        "atr_period": 14,
        "bb_window": 20,
        "bb_std": 2,
        "stoch_k": 14,
        "stoch_d": 3,
    }

    df = df.copy()

    # Ensure column case consistency
    df.columns = df.columns.str.lower()

    if not {'close', 'high', 'low', 'volume'}.issubset(df.columns):
        raise ValueError("DataFrame must contain columns: close, high, low, volume")

    try:
        # RSI
        df[f"rsi_{config['rsi_period']}"] = ta.momentum.RSIIndicator(
            close=df['close'], window=config['rsi_period']
        ).rsi()

        # MACD
        macd = ta.trend.MACD(
            close=df['close'],
            window_slow=config["macd_slow"],
            window_fast=config["macd_fast"],
            window_sign=config["macd_signal"],
        )
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(
            close=df['close'],
            window=config["bb_window"],
            window_dev=config["bb_std"]
        )
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()

        # ATR
        df[f"atr_{config['atr_period']}"] = ta.volatility.AverageTrueRange(
            high=df['high'], low=df['low'], close=df['close'], window=config["atr_period"]
        ).average_true_range()

        # ADX
        df["adx"] = ta.trend.ADXIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=config["adx_period"]
        ).adx()

        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=config["stoch_k"],
            smooth_window=config["stoch_d"]
        )
        df["stoch_k"] = stoch.stoch()
        df["stoch_d"] = stoch.stoch_signal()

    except Exception as e:
        print(f"[ta_calculations] Error applying indicators: {e}")

    return df

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange


def apply_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")

    df = df.copy()

    # RSI
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['rsi_14'] = rsi.rsi()

    # MACD
    macd = MACD(close=df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # Bollinger Bands
    bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_middle'] = bb.bollinger_mavg()

    # ATR
    atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
    df['atr_14'] = atr.average_true_range()

    # Supertrend (custom implementation)
    df['supertrend_direction'], df['supertrend'] = compute_supertrend(df, period=10, multiplier=3)

    # ADX
    adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
    df['adx'] = adx.adx()

    return df


def compute_supertrend(df, period=10, multiplier=3):
    atr = AverageTrueRange(df['High'], df['Low'], df['Close'], window=period).average_true_range()
    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = [np.nan] * len(df)
    direction = [True] * len(df)

    for i in range(period, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i - 1]:
            direction[i] = True
        elif df['Close'].iloc[i] < lowerband.iloc[i - 1]:
            direction[i] = False
        else:
            direction[i] = direction[i - 1]
            if direction[i] and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if not direction[i] and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]

        supertrend[i] = lowerband.iloc[i] if direction[i] else upperband.iloc[i]

    return direction, supertrend

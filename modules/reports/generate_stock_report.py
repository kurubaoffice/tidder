import os
import math
import pandas as pd
import os
from dotenv import load_dotenv
from modules.utils.telegram_sender import send_message
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT_CHAT_ID = os.getenv("CHAT_ID")


import math
import pandas as pd

def interpret_indicators(rsi, macd, macd_signal, supertrend_dir=None, adx=None, atr=None, bb_upper=None, bb_lower=None, close=None):
    sentiment = []

    # Safeguard utility
    def is_valid(val):
        return val is not None and not pd.isna(val) and not (isinstance(val, float) and math.isnan(val))

    # --- RSI Interpretation ---
    if is_valid(rsi):
        if rsi > 70:
            sentiment.append(f"RSI ({rsi:.2f}): Overbought – Possible price correction")
        elif rsi < 30:
            sentiment.append(f"RSI ({rsi:.2f}): Oversold – Possible rebound")
        else:
            sentiment.append(f"RSI ({rsi:.2f}): Neutral – Stock is not overbought/oversold")
    else:
        sentiment.append("RSI: Data not available")

    # --- MACD Interpretation ---
    if is_valid(macd) and is_valid(macd_signal):
        if macd > macd_signal:
            if macd < 0:
                sentiment.append(f"MACD ({macd:.2f}): Bullish crossover – Negative zone, but momentum improving")
            else:
                sentiment.append(f"MACD ({macd:.2f}): Bullish crossover – Positive zone, strong momentum")
        elif macd < macd_signal:
            sentiment.append(f"MACD ({macd:.2f}): Bearish crossover – Momentum weakening")
        else:
            sentiment.append(f"MACD ({macd:.2f}): Neutral – No clear crossover")
    else:
        sentiment.append("MACD: Data not available")

    # --- Supertrend Interpretation ---
    if supertrend_dir is not None:
        direction = "Bullish" if supertrend_dir else "Bearish"
        sentiment.append(f"Supertrend: {direction} Trend")
    else:
        sentiment.append("Supertrend: Data not available")

    # --- ADX Interpretation ---
    if is_valid(adx):
        if adx < 20:
            sentiment.append(f"ADX ({adx:.2f}): Weak trend – Market lacks clear direction")
        elif 20 <= adx <= 40:
            sentiment.append(f"ADX ({adx:.2f}): Developing trend – Growing strength")
        else:
            sentiment.append(f"ADX ({adx:.2f}): Strong trend – Trend strength is high")
    else:
        sentiment.append("ADX: Data not available")

    # --- ATR Interpretation ---
    if is_valid(atr):
        if atr < 1:
            sentiment.append(f"ATR ({atr:.2f}): Low volatility – Stable price")
        elif atr < 5:
            sentiment.append(f"ATR ({atr:.2f}): Moderate volatility – Watch for swings")
        else:
            sentiment.append(f"ATR ({atr:.2f}): High volatility – Risky movement")
    else:
        sentiment.append("ATR: Data not available")

    # --- Bollinger Bands Interpretation ---
    if all(is_valid(v) for v in [bb_upper, bb_lower, close]):
        try:
            close = round(close, 2)
            bb_upper = round(bb_upper, 2)
            bb_lower = round(bb_lower, 2)

            if close > bb_upper:
                sentiment.append(f"Bollinger Bands: 🔴 Overbought (Close {close} > Upper {bb_upper})")
            elif close < bb_lower:
                sentiment.append(f"Bollinger Bands: 🟢 Oversold (Close {close} < Lower {bb_lower})")
            else:
                sentiment.append(f"Bollinger Bands: Within Normal Range (Close {close})")
        except Exception:
            sentiment.append("Bollinger Bands: Calculation error")
    else:
        sentiment.append("Bollinger Bands: Data not available")

    return "\n\n".join(sentiment)





def format_number(value):
    try:
        value = float(value)
        if value >= 1_00_00_00_000:  # 1 Lakh Crores
            return f"₹{value / 1_00_00_00_000:.2f} L Cr"
        elif value >= 1_00_00_000:
            return f"₹{value / 1_00_00_000:.2f} Cr"
        elif value >= 1_00_000:
            return f"₹{value / 1_00_000:.2f} Lakhs"
        else:
            return f"₹{value:.2f}"
    except:
        return "N/A"

def predict_stock_signal(rsi, macd, macd_signal, supertrend_dir=None, adx=None, atr=None, bb_upper=None, bb_lower=None, close=None):
    score = 0
    reasons = []

    # ✅ Check for missing critical values
    indicators = [rsi, macd, macd_signal, supertrend_dir, adx, bb_upper, bb_lower, close]
    if any(val is None or pd.isna(val) for val in indicators[:3]):  # RSI, MACD, MACD signal are minimum required
        return "📉 No Signal: Insufficient data", ["Missing RSI/MACD data"]

    # RSI
    if rsi < 30:
        score += 1
        reasons.append("RSI indicates oversold")
    elif rsi > 70:
        score -= 1
        reasons.append("RSI indicates overbought")

    # MACD
    if macd > macd_signal:
        score += 1
        reasons.append("MACD bullish crossover")
    elif macd < macd_signal:
        score -= 1
        reasons.append("MACD bearish crossover")

    # Supertrend
    if supertrend_dir is not None and not pd.isna(supertrend_dir):
        if supertrend_dir:
            score += 1
            reasons.append("Supertrend bullish")
        else:
            score -= 1
            reasons.append("Supertrend bearish")

    # ADX
    if adx is not None and not pd.isna(adx):
        if adx > 40:
            score += 1
            reasons.append("Strong trend confirmed by ADX")
        elif adx < 20:
            reasons.append("Weak trend by ADX")

    # Bollinger Bands
    if all(v is not None and not pd.isna(v) for v in [bb_upper, bb_lower, close]):
        if close < bb_lower:
            score += 1
            reasons.append("Price below lower Bollinger Band (Oversold)")
        elif close > bb_upper:
            score -= 1
            reasons.append("Price above upper Bollinger Band (Overbought)")

    # Final decision
    if score >= 3:
        signal = "🟢 Strong Buy"
    elif score == 2:
        signal = "✅ Buy"
    elif score == 1:
        signal = "⚪ Watchlist"
    elif score <= -2:
        signal = "🔴 Strong Sell"
    else:
        signal = "⚠️ Neutral"

    return signal, reasons


def generate_verdict(rsi=None, macd=None, macd_signal=None, supertrend=None, adx=None, atr=None, bb_upper=None, bb_lower=None, close=None):
    score = 0
    total_possible = 0
    comments = []

    def is_valid(v):
        return v is not None and not pd.isna(v)

    # --- RSI ---
    if is_valid(rsi):
        total_possible += 1
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1

    # --- MACD ---
    if is_valid(macd) and is_valid(macd_signal):
        total_possible += 1
        if macd > macd_signal:
            score += 1
        elif macd < macd_signal:
            score -= 1

    # --- Supertrend ---
    if supertrend is not None:
        total_possible += 1
        score += 1 if supertrend else -1

    # --- ADX (strength only) ---
    if is_valid(adx):
        total_possible += 1
        if adx > 20:
            score += 1

    # --- Bollinger Bands ---
    if all(is_valid(v) for v in [bb_upper, bb_lower, close]):
        total_possible += 1
        if close < bb_lower:
            score += 1
        elif close > bb_upper:
            score -= 1

    # Confidence is based on how many valid indicators were used
    if total_possible == 0:
        return "❓ Verdict: Not enough data for signal confidence."

    confidence = round((abs(score) / total_possible) * 100)
    signal = "Neutral"

    if score >= 3:
        signal = "🟢 Strong Buy"
    elif score == 2:
        signal = "🟢 Buy"
    elif score == 1:
        signal = "🟡 Mild Bullish"
    elif score == 0:
        signal = "⚪ Neutral"
    elif score == -1:
        signal = "🟠 Mild Bearish"
    elif score == -2:
        signal = "🔴 Sell"
    elif score <= -3:
        signal = "🔴 Strong Sell"

    return f"{signal} (Confidence: {confidence}%)"



def format_percentage(value):
    try:
        return f"{float(value) * 100:.2f}%"
    except:
        return "N/A"

def generate_report(symbol, company_csv_path=None, tech_csv_path=None):
    """
    Generate formatted report string for a given stock symbol
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Set default paths
    if not company_csv_path:
        company_csv_path = os.path.join(base_dir, "data", "processed", "company_info.csv")
    if not tech_csv_path:
        tech_csv_path = os.path.join(base_dir, "data", "processed", "technical_indicators.csv")

    if not os.path.exists(company_csv_path) or not os.path.exists(tech_csv_path):
        print(f"Missing CSVs. Ensure both company_info.csv and technical_indicators.csv are present.")
        return None


    # Read both CSVs
    comp_df = pd.read_csv(company_csv_path)
    tech_df = pd.read_csv(tech_csv_path)

    comp_df.columns = [col.lower() for col in comp_df.columns]
    tech_df.columns = [col.lower() for col in tech_df.columns]

    comp_row = comp_df[comp_df["symbol"].str.upper() == symbol.upper()]
    tech_row = tech_df[tech_df["symbol"].str.upper() == symbol.upper()]

    if comp_row.empty:
        print(f"[WARN] No company info found for symbol: {symbol}")
        return None
    if tech_row.empty:
        print(f"[WARN] No technical data found for symbol: {symbol}")
        return None

    comp_row = comp_row.iloc[0]
    tech_row = tech_row.iloc[0]

    # Extract indicators for summary
    try:
        def safe_float(val):
            try:
                fval = float(val)
                return fval if not math.isnan(fval) else None
            except:
                return None

        rsi = safe_float(tech_row.get("rsi_14"))
        macd = safe_float(tech_row.get("macd"))
        macd_signal = safe_float(tech_row.get("macd_signal"))
        adx = safe_float(tech_row.get("adx"))
        atr = safe_float(tech_row.get("atr_14"))
        bb_upper = safe_float(tech_row.get("bb_upper"))
        bb_lower = safe_float(tech_row.get("bb_lower"))
        close = safe_float(tech_row.get("close"))

        supertrend_col = [col for col in tech_row.index if col.startswith('supertrend_') and col.endswith('_dir')]
        supertrend_val = tech_row.get(supertrend_col[0]) if supertrend_col else None
        if isinstance(supertrend_val, str):
            supertrend_val = supertrend_val.lower() == 'true'
        elif isinstance(supertrend_val, (bool, int)):
            supertrend_val = bool(supertrend_val)
        else:
            supertrend_val = None

        indicator_summary = interpret_indicators(
            rsi, macd, macd_signal,
            supertrend_val, adx, atr,
            bb_upper=bb_upper, bb_lower=bb_lower, close=close
        )
        # Predict signal
        signal, reasons = predict_stock_signal(
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            supertrend_dir=supertrend_val,
            adx=adx,
            atr=atr,
            bb_upper=bb_upper,
            bb_lower=bb_lower,
            close=close
        )

        verdict = generate_verdict(
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            supertrend=supertrend_val,
            adx=adx,
            atr=atr,
            bb_upper=bb_upper,
            bb_lower=bb_lower,
            close=close
        )

        # Append to report
        indicator_summary += f"\n\n🔮 Signal: {signal}"
        if reasons:
            indicator_summary += "\n\n📌 Reason:\n" + "\n".join(f"- {r}" for r in reasons)
        indicator_summary += f"\n\n🧠 Verdict: {verdict}"

    except Exception as e:
        print(f"[ERROR] Failed to interpret indicators: {e}")
        indicator_summary = "N/A"

    # Report formatting
    report = f"""
Stock Report: {symbol}

+----------------------+----------------------------+
       Company Info                          
+----------------------+----------------------------+
 Name                 : {comp_row.get('companyname', 'N/A')}
 Sector               : {comp_row.get('sector', 'N/A')}
 Industry             : {comp_row.get('industry', 'N/A')}
 Market Cap           : {format_number(comp_row.get('marketcap'))}
 P/E Ratio            : {comp_row.get('pe', 'N/A')}
 Book Value           ; {comp_row.get('bookvalue', 'N/A')}
 ROE                  ; {format_percentage(comp_row.get('roe'))}
 ROCE                 : {format_percentage(comp_row.get('roce'))}
 Total Debt           ; {format_number(comp_row.get('debt'))}
+----------------------+----------------------------+
          Technical Indicators                      
+----------------------+----------------------------+
 RSI (14)             : {round(float(tech_row.get('rsi_14', 0.0)), 2)}
 MACD                : {round(float(tech_row.get('macd', 0.0)), 2)}
 MACD Signal         : {round(float(tech_row.get('macd_signal', 0.0)), 2)}
 Supertrend          : {'🟢 Buy' if supertrend_val else '🔴 Sell' if supertrend_val is not None else '⚪ N/A'}
 ADX Strength         : {round(float(tech_row.get('adx', 0.0)), 2)}
 BB Upper Band        : {round(float(tech_row.get('bb_upper', 0.0)), 2)}
 BB Lower Band        : {round(float(tech_row.get('bb_lower', 0.0)), 2)}
 ATR (Volatility)     ; {round(float(tech_row.get('atr_14', 0.0)), 2)}
+----------------------+----------------------------+

      📊 Technical Summary
+----------------------+----------------------------+
{indicator_summary}

Source: Yahoo Finance
""".strip()

    return report

def generate_reports_for_symbols(symbols, company_csv_path=None, tech_csv_path=None, send_to_telegram=False, chat_id=None):
    reports = []
    for symbol in symbols:
        print(f"Generating report for: {symbol}")
        report = generate_report(symbol, company_csv_path, tech_csv_path)
        if report:
            reports.append(report)
            if send_to_telegram and chat_id:
                send_message(chat_id, report)
    return reports

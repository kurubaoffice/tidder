from modules.utils.telegram_sender import send_message
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()
DEFAULT_CHAT_ID = os.getenv("CHAT_ID")

import os

import pandas as pd
import numpy as np
import math

def interpret_indicators(rsi, macd, macd_signal, supertrend_dir=None, adx=None, atr=None,
                         bb_upper=None, bb_lower=None, close=None, tech_row=None):
    sentiment = []
    insights = []
    summary = []

    def is_valid(val):
        return val is not None and not pd.isna(val) and not (isinstance(val, float) and math.isnan(val))

    try:
        # Extract from tech_row if values are not directly passed
        if tech_row is not None:
            print(f"[DEBUG] Last row in interpret_indicators:\n{tech_row}")

            # --- Supertrend ---
            if supertrend_dir is None:
                st_cols = [col for col in tech_row.index if col.startswith("supertrend_") and col.endswith("_dir")]
                if st_cols:
                    raw_val = tech_row.get(st_cols[0])
                    print(f"[DEBUG] Supertrend column: {st_cols[0]}, Raw value: {raw_val}")
                    if isinstance(raw_val, str):
                        supertrend_dir = raw_val.strip().lower() == 'true'
                    elif isinstance(raw_val, (bool, int, float, np.bool_)):
                        supertrend_dir = bool(raw_val)
                    print(f"[DEBUG] Final Supertrend direction: {supertrend_dir}")
                    print(f"[DEBUG] tech_row keys: {list(tech_row.index)}")
                    print("[DEBUG] tech_row columns:", list(tech_row.index if tech_row is not None else []))

                # --- ADX ---
                if adx is None:
                    print(f"[DEBUG] tech_row keys: {list(tech_row.index)}")
                    adx_cols = [col for col in tech_row.index if 'adx' in col.lower()]
                    print(f"[DEBUG] Found ADX columns: {adx_cols}")
                    if adx_cols:
                        raw_adx = tech_row.get(adx_cols[0])
                        print(f"[DEBUG] Raw ADX = {raw_adx} | type = {type(raw_adx)}")
                        if is_valid(raw_adx):
                            adx = float(raw_adx)
                            print(f"[DEBUG] Final ADX extracted = {adx}")
                        else:
                            print("[WARN] ADX value was invalid or NaN.")
                    else:
                        print("[WARN] No ADX column found in tech_row.")

    finally:
        print("✅ Finished processing Supertrend and ADX.")

    # --- Supertrend Interpretation ---
    if supertrend_dir is not None:
        direction = "Bullish" if supertrend_dir else "Bearish"
        sentiment.append(f"Supertrend: {direction} Trend")
        summary.append(f"{'🔼' if supertrend_dir else '🔽'} Supertrend indicates **{direction}**.")
    else:
        sentiment.append("Supertrend: Data not available")
        summary.append("⚠️ Supertrend not available.")

    # --- ADX Interpretation ---
    if is_valid(adx):
        if adx < 20:
            sentiment.append(f"ADX ({adx:.2f}): Weak trend – Market lacks clear direction")
            summary.append(f"😐 ADX ({adx:.1f}) suggests a **weak trend**.")
        elif 20 <= adx <= 40:
            sentiment.append(f"ADX ({adx:.2f}): Developing trend – Growing strength")
            summary.append(f"📊 ADX ({adx:.1f}) indicates a **moderate trend**.")
        else:
            sentiment.append(f"ADX ({adx:.2f}): Strong trend – Trend strength is high")
            summary.append(f"💪 ADX ({adx:.1f}) indicates a **strong trend**.")
    else:
        sentiment.append("ADX: Data not available")
        summary.append("⚠️ ADX not available.")

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

    return "\n".join(sentiment + [""] + summary)

    # return "\n\n".join(sentiment)


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


def predict_stock_signal(rsi, macd, macd_signal, supertrend_dir=None, adx=None, atr=None, bb_upper=None, bb_lower=None,
                         close=None):
    score = 0
    reasons = []

    # ✅ Check for missing critical values
    indicators = [rsi, macd, macd_signal, supertrend_dir, adx, bb_upper, bb_lower, close]
    if any(val is None or pd.isna(val) for val in indicators[:4]):  # RSI, MACD, MACD signal are minimum required
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


def generate_verdict(rsi=None, macd=None, macd_signal=None, supertrend=None, adx=None, atr=None, bb_upper=None,
                     bb_lower=None, close=None):
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


def extract_float(row, key):
    try:
        val = row.get(key, None)
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        return round(float(val), 2)
    except:
        return None


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

    # Load data
    company_df = pd.read_csv(company_csv_path)
    tech_df = pd.read_csv(tech_csv_path)

    # Filter for the symbol (case-insensitive)
    company_info = company_df[company_df["symbol"].str.upper() == symbol.upper()]
    tech_info = tech_df[tech_df["symbol"].str.upper() == symbol.upper()]

    if company_info.empty or tech_info.empty:
        return f"No data found for symbol: {symbol}"

    latest_tech = tech_info.sort_values("date").iloc[-1]  # last row for most recent indicators

    # Extract indicators
    rsi = latest_tech.get("rsi_14", "N/A")
    macd = latest_tech.get("macd", "N/A")
    macd_signal = latest_tech.get("macd_signal", "N/A")
    bb_upper = latest_tech.get("bb_upper", "N/A")
    bb_lower = latest_tech.get("bb_lower", "N/A")
    close_price = latest_tech.get("close", "N/A")

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
    tech_row = tech_row.sort_values("date").iloc[-1]

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
        supertrend = tech_row.get("supertrend_direction")
        adx = extract_float(tech_row, "adx_14")
        atr = safe_float(tech_row.get("atr_14"))
        bb_upper = safe_float(tech_row.get("bb_upper"))
        bb_lower = safe_float(tech_row.get("bb_lower"))
        close = safe_float(tech_row.get("close"))

        # --- Extract Supertrend Direction (safe bool conversion) ---
        supertrend_val = None
        supertrend_col = [col for col in tech_row.index if col.startswith('supertrend_') and col.endswith('_dir')]
        print("🛠️ Supertrend matching columns:", supertrend_col)
        if supertrend_col:
            raw_val = tech_row.get(supertrend_col[0])
            print("📦 Raw supertrend_val from DataFrame:", raw_val, "| type:", type(raw_val))
            try:
                if isinstance(raw_val, str):
                    supertrend_val = raw_val.strip().lower() == 'true'
                elif isinstance(raw_val, (bool, int, np.bool_)):  # <-- updated this line
                    supertrend_val = bool(raw_val)
                else:
                    print("⚠️ Unrecognized type for supertrend_val")
            except Exception as e:
                print("❌ Error processing supertrend_val:", e)
        print("✅ Final processed supertrend_val (bool):", supertrend_val)
        print(f"[DEBUG] interpret_indicators: ADX value received = {adx} | type: {type(adx)}")

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

        def format_number(val):
            if val is None or pd.isna(val):
                return "N/A"
            return f"{val:,.2f}"

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
Current Price : {format_number(comp_row.get("currentPrice"))}
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
 ADX Strength         : {round(float(tech_row.get('adx_14', 0.0)), 2)}
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


def generate_reports_for_symbols(symbols, company_csv_path=None, tech_csv_path=None, send_to_telegram=False,
                                 chat_id=None):
    reports = []
    for symbol in symbols:
        print(f"Generating report for: {symbol}")
        report = generate_report(symbol, company_csv_path, tech_csv_path)
        if report:
            reports.append(report)
            if send_to_telegram and chat_id:
                send_message(chat_id, report)
    return reports

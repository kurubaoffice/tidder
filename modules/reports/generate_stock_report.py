import os
import pandas as pd
from modules.utils.telegram_bot import send_message

def interpret_indicators(rsi, macd, macd_signal, supertrend_dir=None, adx=None):
    sentiment = []

    # RSI Interpretation
    if rsi > 70:
        sentiment.append(f"RSI ({rsi:.2f}): Overbought – Possible price correction")
    elif rsi < 30:
        sentiment.append(f"RSI ({rsi:.2f}): Oversold – Possible rebound")
    else:
        sentiment.append(f"RSI ({rsi:.2f}): Neutral – Stock is not overbought/oversold")

    # MACD Interpretation
    if macd > macd_signal:
        if macd < 0:
            sentiment.append(f"MACD ({macd:.2f}): Bullish crossover – Negative zone, but momentum improving")
        else:
            sentiment.append(f"MACD ({macd:.2f}): Bullish crossover – Positive zone, strong momentum")
    elif macd < macd_signal:
        sentiment.append(f"MACD ({macd:.2f}): Bearish crossover – Momentum weakening")
    else:
        sentiment.append(f"MACD ({macd:.2f}): Neutral – No clear crossover")

    # Supertrend interpretation
    if supertrend_dir is not None:
        direction = "Bullish" if supertrend_dir else "Bearish"
        sentiment.append(f"Supertrend: {direction} Trend")

    # ADX Interpretation
    if adx is not None:
        if adx < 20:
            sentiment.append(f"ADX ({adx:.2f}): Weak trend – Market lacks clear direction")
        elif 20 <= adx <= 40:
            sentiment.append(f"ADX ({adx:.2f}): Developing trend – Growing strength")
        else:
            sentiment.append(f"ADX ({adx:.2f}): Strong trend – Trend strength is high")

    return "\n".join(sentiment)




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
        rsi = float(tech_row.get("rsi_14", "nan"))
        macd = float(tech_row.get("macd", "nan"))
        macd_signal = float(tech_row.get("macd_signal", "nan"))
        supertrend_col = [col for col in tech_row.index if col.startswith('supertrend_') and col.endswith('_dir')]
        supertrend_val = tech_row.get(supertrend_col[0]) if supertrend_col else None
        #Normalize Supertrend value to boolean
        if isinstance(supertrend_val, str):
            supertrend_val = supertrend_val.lower() == 'true'
        adx = float(tech_row.get("adx", "nan"))
        indicator_summary = interpret_indicators(round(rsi, 2), round(macd, 2), round(macd_signal, 2), supertrend_val, round(adx, 2))
    except:
        indicator_summary = "N/A"

    # Report formatting
    report = f"""
Stock Report: {symbol}

Company Info:
Name:                {comp_row.get('companyname', 'N/A')}
Sector:              {comp_row.get('sector', 'N/A')}
Industry:            {comp_row.get('industry', 'N/A')}
Market Cap:          {format_number(comp_row.get('marketcap'))}
P/E Ratio:           {comp_row.get('pe', 'N/A')}
Book Value:          {comp_row.get('bookvalue', 'N/A')}
ROE:                 {format_percentage(comp_row.get('roe'))}
ROCE:                {format_percentage(comp_row.get('roce'))}
Total Debt:          {format_number(comp_row.get('debt'))}

Technical Indicators:
RSI (14):            {round(float(tech_row.get('rsi_14', 0.0)), 2)}
MACD:                {round(float(tech_row.get('macd', 0.0)), 2)}
MACD Signal:         {round(float(tech_row.get('macd_signal', 0.0)), 2)}
Supertrend:          {'Buy' if supertrend_val else 'Sell' if supertrend_val is not None else 'N/A'}
ADX (14):            {round(float(tech_row.get('adx', 0.0)), 2)}
Bollinger Upper:     {round(float(tech_row.get('bb_upper', 0.0)), 2)}
Bollinger Lower:     {round(float(tech_row.get('bb_lower', 0.0)), 2)}
ATR:                 {round(float(tech_row.get('atr', 0.0)), 2)}

📊 Technical Summary:
{indicator_summary}

Source: Yahoo Finance
""".strip()

    return report

def generate_reports_for_symbols(symbols, company_csv_path=None, tech_csv_path=None, send_to_telegram=False):
    reports = []
    for symbol in symbols:
        print(f"Generating report for: {symbol}")
        report = generate_report(symbol, company_csv_path, tech_csv_path)
        if report:
            reports.append(report)
            if send_to_telegram:
                send_message(report)
    return reports

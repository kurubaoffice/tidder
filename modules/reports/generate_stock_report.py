# modules/reports/generate_stock_report.py

import os
import pandas as pd
from modules.utils.telegram_bot import send_message


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


def generate_report(symbol, csv_path=None):
    """
    Generate formatted report string for a given stock symbol
    """
    if not csv_path:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        csv_path = os.path.join(base_dir, "data", "processed", "company_info.csv")

    if not os.path.exists(csv_path):
        print(f"Company info CSV not found at: {csv_path}")
        return None

    df = pd.read_csv(csv_path)
    company_data = df[df["symbol"].str.upper() == symbol.upper()]
    if company_data.empty:
        print(f"No data found for symbol: {symbol}")
        return None

    row = company_data.iloc[0]

    report = f"""
Stock Report: {row['symbol']}

Company Name:        {row.get('companyName', 'N/A')}
Sector:              {row.get('sector', 'N/A')}
Industry:            {row.get('industry', 'N/A')}
Market Cap:          {format_number(row.get('marketCap'))}
P/E Ratio:           {row.get('pe', 'N/A')}
Book Value:          {row.get('bookValue', 'N/A')}
ROE:                 {format_percentage(row.get('roe'))}
ROCE:                {format_percentage(row.get('roce'))}
Total Debt:          {format_number(row.get('debt'))}


Source: Yahoo Finance
""".strip()
    return report


def generate_reports_for_symbols(symbols, csv_path=None, send_to_telegram=False):
    reports = []
    for symbol in symbols:
        print(f"Generating report for: {symbol}")
        report = generate_report(symbol, csv_path)
        if report:
            reports.append(report)
            if send_to_telegram:
                send_message(report)
    return reports

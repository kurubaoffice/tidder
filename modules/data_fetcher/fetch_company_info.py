# modules/data_fetcher/fetch_company_info.py

import os
import pandas as pd
import yfinance as yf
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)



def fetch_company_info(symbol):
    info = {}
    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info
        info_cleaned = {
            "symbol": symbol.upper(),
            "companyName": info.get("longName"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "marketCap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "bookValue": info.get("bookValue"),
            "faceValue": info.get("faceValue", "N/A"),
            "roe": info.get("returnOnEquity", "N/A"),
            "roce": info.get("returnOnAssets", "N/A"),  # closest to ROCE
            "debt": info.get("totalDebt", "N/A"),
            "promoterHolding": "N/A",  # Not in yfinance
            "isin": info.get("isin", "N/A")  # Rare, often missing
        }

        # Add all other available fields
        for k, v in info.items():
            if k not in info_cleaned:
                info_cleaned[k] = v

        return info_cleaned

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def save_company_info(symbols):
    rows = []
    for symbol in symbols:
        print(f"Fetching: {symbol}")
        data = fetch_company_info(symbol)
        if data:
            rows.append(data)

    if rows:
        df = pd.DataFrame(rows)
        output_path = os.path.join(OUTPUT_DIR, "company_info.csv")
        df.to_csv(output_path, index=False)
        print(f"\nSaved to CSV at: {output_path}")
    else:
        print("No data to save.")


#if __name__ == "__main__":
#    stock_list = ["EPACK"]  # Replace with your list
#   save_company_info(stock_list)

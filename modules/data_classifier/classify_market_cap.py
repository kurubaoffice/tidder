# modules/data_classifier/classify_market_cap.py

import pandas as pd
from nsepython import nse_eq
import os
import time

def classify_market_caps(input_path="data/raw/nifty500_companies.csv", output_path="data/processed/classified_market_caps.csv"):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    if df.empty:
        raise ValueError("Input CSV is empty.")

    classified_data = []

    for idx, row in df.iterrows():
        symbol = row["symbol"]
        try:
            eq_data = nse_eq(symbol)
            market_cap_str = eq_data["info"].get("marketCap", "0").replace(",", "")
            market_cap = float(market_cap_str)
        except Exception as e:
            print(f"[{symbol}] Error fetching data: {e}")
            market_cap = 0.0

        # Market cap classification (adjust thresholds as needed)
        if market_cap >= 200000:  # in crores (e.g., ₹2 lakh Cr)
            cap_type = "Large Cap"
        elif market_cap >= 50000:
            cap_type = "Mid Cap"
        else:
            cap_type = "Small Cap"

        classified_data.append({
            "symbol": symbol,
            "company_name": row.get("company_name", ""),
            "isin": row.get("isin", ""),
            "industry": row.get("industry", ""),
            "market_cap": market_cap,
            "cap_category": cap_type
        })

        # Be polite to NSE servers
        time.sleep(0.6)

    output_df = pd.DataFrame(classified_data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)
    print(f"✅ Classified market caps saved to {output_path}")
    return output_df

if __name__ == "__main__":
    df = classify_market_caps()
    print(df.head())

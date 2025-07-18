# modules/data_fetcher/fetch_companies.py
import pandas as pd
import os
import requests
from io import StringIO


def fetch_and_save_companies(url, output_file, filter_series="EQ"):
    print(f"Downloading: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data from {url} - Status Code: {response.status_code}")
        return None

    df = pd.read_csv(StringIO(response.text))

    # Normalize column names to simplify access
    df.columns = [col.strip().upper().replace(" ", "_") for col in df.columns]

    if filter_series and "SERIES" in df.columns:
        df = df[df["SERIES"] == filter_series]

    if "SYMBOL" not in df.columns or ("NAME_OF_COMPANY" not in df.columns and "NAME_OF_COMPANY" not in df.columns):
        print(f"Unexpected CSV format. Columns found: {df.columns.tolist()}")
        return None

    # Rename appropriate company name column to 'name'
    if "NAME_OF_COMPANY" in df.columns:
        df = df.rename(columns={"NAME_OF_COMPANY": "name"})
    elif "NAME__OF__COMPANY" in df.columns:
        df = df.rename(columns={"NAME__OF__COMPANY": "name"})

    df = df.rename(columns={"SYMBOL": "symbol"})

    # Select and sort
    df = df[["symbol", "name"]].sort_values(by="symbol")

    # Save to CSV
    output_path = os.path.join("data", "raw", output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} companies to {output_path}")
    return df




def get_all_companies():
    print("Fetching main board companies...")
    main_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    try:
        main_df = fetch_and_save_companies(main_url, "listed_companies.csv")
    except Exception as e:
        print(f"Error fetching main board: {e}")
        return

    print("Fetching SME board companies...")
    sme_url = "https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv"
    try:
        sme_df = fetch_and_save_companies(sme_url, "listed_sme_companies.csv", filter_series=None)
    except Exception as e:
        print(f"Error fetching SME board: {e}")
        return

    return main_df, sme_df


if __name__ == "__main__":
    main_df, sme_df = get_all_companies()
    print(f"Fetched {len(main_df)} main board companies.")
    print(main_df.head())

    print(f"\nFetched {len(sme_df)} SME companies.")
    print(sme_df.head())

# File: modules/data_fetcher/snapshot_indices.py

import os
import requests
import pandas as pd
from urllib.parse import quote
from datetime import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com"
}

# Step 1: Set global path to data/raw/snapshots/indices
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SNAPSHOT_DIR = os.path.join(PROJECT_ROOT, "data", "snapshots", "indices")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# Step 2: NSE Indices you want to snapshot
INDEX_LIST = [
    "NIFTY 50", "NIFTY AUTO"
    # Add more if needed
]

def fetch_index_snapshot(index_name, session) -> pd.DataFrame:
    """Fetch index data from NSE."""
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={quote(index_name)}"
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return pd.DataFrame(response.json().get("data", []))
        else:
            print(f"[{index_name}] HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"[{index_name}] Error: {e}")
    return None

def snapshot_all_indices():
    """Fetch and save daily snapshot for each index."""
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"Session Init Error: {e}")
        return

    today_str = datetime.today().strftime("%Y-%m-%d")

    for index in INDEX_LIST:
        print(f"Fetching: {index}")
        df = fetch_index_snapshot(index, session)
        if df is not None and not df.empty:
            file_name = f"{index.lower().replace(' ', '_')}_{today_str}.csv"
            save_path = os.path.join(SNAPSHOT_DIR, file_name)
            df.to_csv(save_path, index=False)
            print(f"Saved {len(df)} rows → {save_path}")
        else:
            print(f"No data for: {index}")
        time.sleep(10)  # Increase delay to reduce risk of blocking

if __name__ == "__main__":
    snapshot_all_indices()

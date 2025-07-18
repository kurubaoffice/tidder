import os
import requests
import pandas as pd
from urllib.parse import quote
import time

# Step 1: Set correct global data/raw path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 2: NSE index list
INDEX_LIST = [
    "NIFTY 50", "NIFTY AUTO"
]

# Step 3: Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}

# Step 4: Fetch data with error handling
def fetch_index_data(index_name, session):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={quote(index_name)}"
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json().get("data", [])
                return pd.DataFrame(data)
            except Exception:
                print(f"Non-JSON response for: {index_name}")
        else:
            print(f"Failed to fetch: {index_name} | HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching {index_name}: {e}")
    return None

def main():
    session = requests.Session()

    # Step 5: Initialize session by visiting homepage (important for cookies)
    try:
        home = session.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
        time.sleep(20)  # give cookies time to settle
    except Exception as e:
        print(f"Session init failed: {e}")
        return

    for index in INDEX_LIST:
        print(f"Fetching: {index}")
        df = fetch_index_data(index, session)
        if df is not None and not df.empty:
            file_name = index.lower().replace(" ", "_").replace("&", "and") + ".csv"
            file_path = os.path.join(OUTPUT_DIR, file_name)
            df.to_csv(file_path, index=False)
            print(f"Saved {len(df)} rows to {file_path}")
        else:
            print(f"No data for: {index}")
        time.sleep(20)

if __name__ == "__main__":
    main()

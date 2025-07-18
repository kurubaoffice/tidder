import sys
import os

# Ensure project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher.fetch_companies import get_all_companies
from modules.data_fetcher.snapshot_indices import snapshot_all_indices  # Uncomment when ready
from modules.data_fetcher.fetch_company_info import fetch_company_info
from modules.reports.generate_stock_report import generate_reports_for_symbols

def main():
    # Fetch all companies (Main board + SME)
   # main_df, sme_df = get_all_companies()

    #print(f"Fetched {len(main_df)} main board companies.")
    #print(main_df.head())

    #print(f"\nFetched {len(sme_df)} SME companies.")
    #print(sme_df.head())

    # --- Optional: Add snapshot functionality ---
   # snapshot_all_indices()
    symbols = ["EPACK"]
    results = []

    for symbol in symbols:
        print(f"Fetching info: {symbol}")
        info = fetch_company_info(symbol)
        if info:
            results.append(info)



    from modules.reports.generate_stock_report import generate_report
    report = generate_report("EPACK")
    if report:
        print(report)
    stock_list = ["EPACK"]
    generate_reports_for_symbols(stock_list, send_to_telegram=True)

if __name__ == "__main__":
    main()

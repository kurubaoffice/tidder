import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher.fetch_company_info import fetch_company_info
from modules.indicators.indicators import process_and_save_indicators
from modules.reports.generate_stock_report import generate_reports_for_symbols

def main():
    symbols = ["EPACK"]

    # Step 1: Process indicators (fetches OHLCV, calculates indicators, saves to CSV)
    for symbol in symbols:
        print(f"[1] Processing indicators for {symbol}")
        process_and_save_indicators(symbol)  # <--- This MUST be called BEFORE generating reports

    # Step 2: Fetch and store company info
    for symbol in symbols:
        print(f"[2] Fetching company info for {symbol}")
        fetch_company_info(symbol)

    # Step 3: Generate and send reports
    print(f"[3] Generating and sending report...")
    generate_reports_for_symbols(symbols, send_to_telegram=True)

if __name__ == "__main__":
    main()

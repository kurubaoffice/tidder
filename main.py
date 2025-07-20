import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher.fetch_company_info import save_company_info
from modules.indicators.indicators import process_and_save_indicators
from modules.reports.generate_stock_report import generate_reports_for_symbols
#from modules.utils.symbol_mapper import get_symbol_from_name  # You create this

def run_pipeline_for_company_name(company_name):
    symbol = get_symbol_from_name(company_name)
    if not symbol:
        print(f"[WARN] No symbol found for: {company_name}")
        return False

    try:
        print(f"[1] Processing indicators for {symbol}")
        process_and_save_indicators(symbol)

        print(f"[2] Fetching and saving company info for {symbol}")
        save_company_info([symbol])

        print(f"[3] Generating and sending report for {symbol}")
        generate_reports_for_symbols([symbol], send_to_telegram=True)
        return True
    except Exception as e:
        print(f"[ERROR] Pipeline failed for {symbol}: {e}")
        return False

def run_pipeline_for_symbol(symbol, chat_id=None):
    try:
        print(f"[1] Processing indicators for {symbol}")
        process_and_save_indicators(symbol)

        print(f"[2] Fetching company info for {symbol}")
        save_company_info([symbol])

        print(f"[3] Generating and sending report...")
        generate_reports_for_symbols([symbol], send_to_telegram=True, chat_id=chat_id)

        return True
    except Exception as e:
        print(f"[ERROR] Pipeline failed for {symbol}: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Pipeline failed for {symbol}: {e}")
        return False
def get_symbol_from_name(company_name, csv_path="data/raw/listed_companies.csv"):
    try:
        df = pd.read_csv(csv_path)

        # Normalize both sides for robust comparison
        company_name = company_name.strip().lower()
        df["name_lower"] = df["name"].str.lower().str.strip()

        # Exact match
        match = df[df["name_lower"] == company_name]
        if not match.empty:
            return match.iloc[0]["symbol"]

        # Partial match fallback (optional)
        partial = df[df["name_lower"].str.contains(company_name)]
        if not partial.empty:
            return partial.iloc[0]["symbol"]

        return None
    except Exception as e:
        print(f"[ERROR] Failed to read symbol from name: {e}")
        return None

def main():
    run_pipeline_for_symbol("TATAMOTORS")  # Default/manual run

if __name__ == "__main__":
    main()

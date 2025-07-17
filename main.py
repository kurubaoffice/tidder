# main.py

from modules.data_fetcher.fetch_companies import get_all_companies
from modules.data_fetcher.classify_market_cap import classify_companies
from modules.indicators.compute_signals import evaluate_signals
from modules.reports.report_generator import create_report
from modules.reports.notifier import send_report


def main():
    companies = get_all_companies()
    classified = classify_companies(companies)

    for cap_type, group in classified.items():
        for company in group:
            result = evaluate_signals(company)
            if result["signal"]:
                report = create_report(company, result)
                send_report(report, method="telegram")


if __name__ == "__main__":
    main()

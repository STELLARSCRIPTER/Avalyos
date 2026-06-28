# Script to generate synthetic company risk dataset (500 rows)
# This file is created temporarily to generate the CSV and will not be shown in outputs.
import csv
from math import fmod

OUT = 'data_company_risk_500.csv'
N = 500

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    writer = csv.writer(fh)
    writer.writerow([
        'company_id', 'company_name',
        'revenue', 'profit', 'debt', 'assets',
        'downtime_hours_per_month', 'failure_rate_per_1000', 'vendor_delay_days_per_month',
        'default_history', 'avg_days_to_pay', 'credit_score',
        'esg_environment', 'esg_governance', 'esg_controversies',
        'market_volatility', 'stock_return_30d',
        'risk_score', 'default_probability'
    ])

    for i in range(1, N+1):
        company_id = f"C{i:05d}"
        company_name = f"Company {i:04d}"
        # revenue between ~1M and ~100M (pseudo-random deterministic)
        revenue = 1_000_000 + ((i * 12345) % 99_000_000)
        # profit margin between -10% and +39%
        profit_margin = ((i * 37) % 50) - 10
        profit = int(revenue * (profit_margin / 100.0))
        debt_ratio = 0.10 + ((i * 19) % 80) / 100.0  # 0.10 - 0.89
        debt = int(revenue * debt_ratio)
        assets = int(revenue * (1.0 + ((i * 13) % 300) / 100.0))

        downtime_hours = ((i * 7) % 200)
        failure_rate = ((i * 11) % 200) / 10.0
        vendor_delay = ((i * 5) % 30)

        default_history = 1 if ((i * 29) % 100) < 5 else 0
        avg_days_to_pay = 15 + ((i * 23) % 90)
        credit_score = 300 + ((i * 31) % 551)  # 300-850

        esg_environment = 20 + ((i * 41) % 81)
        esg_governance = 20 + ((i * 43) % 81)
        esg_controversies = (i * 17) % 11

        market_volatility = round(0.01 + ((i * 3) % 100) / 100.0, 4)
        stock_return_30d = round(-0.5 + ((i * 13) % 1000) / 1000.0, 4)

        # risk_score heuristic (0..1)
        debt_to_assets = debt / assets if assets > 0 else 1.0
        profit_ratio = profit / revenue if revenue != 0 else -1.0
        credit_norm = (credit_score - 300) / 550.0  # 0..1
        esg_mean = (esg_environment + esg_governance) / 2.0 / 100.0

        raw = (
            0.40 * debt_to_assets +
            0.18 * (1.0 - max(min(profit_ratio, 0.3), -0.3) / 0.3) +
            0.12 * (downtime_hours / 200.0) +
            0.08 * (failure_rate / 20.0) +
            0.06 * (vendor_delay / 30.0) +
            0.10 * (1.0 - credit_norm) +
            0.04 * (1.0 - esg_mean) +
            0.02 * market_volatility +
            0.0 * default_history
        )
        # clamp
        risk_score = max(0.0, min(1.0, round(raw, 4)))
        # default probability increased if default_history or very poor credit
        default_probability = round(min(1.0, 0.02 + 0.45 * risk_score + 0.2 * default_history + (0 if credit_score>650 else 0.1)), 4)

        writer.writerow([
            company_id, company_name,
            revenue, profit, debt, assets,
            downtime_hours, failure_rate, vendor_delay,
            default_history, avg_days_to_pay, credit_score,
            esg_environment, esg_governance, esg_controversies,
            market_volatility, stock_return_30d,
            risk_score, default_probability
        ])

print(f"Wrote {N} rows to {OUT}")

"""
Run the full analysis: clean -> analyse (Pandas + SQL) -> charts -> reports.

    python run_analysis.py

Everything is written to the outputs/ folder.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import analysis as a  # noqa: E402
import charts  # noqa: E402
from clean import clean, load_raw, quality_report_markdown, with_customers  # noqa: E402
from sql_analysis import run_all  # noqa: E402

OUT = ROOT / "outputs"
CHARTS = OUT / "charts"


def main():
    CHARTS.mkdir(parents=True, exist_ok=True)

    print("1/5 Loading and cleaning data...")
    raw = load_raw()
    sales, cancellations, report = clean(raw)
    customers = with_customers(sales)
    (OUT / "data_quality_report.md").write_text(
        "# Data quality report\n\n" + quality_report_markdown(raw, report, sales) + "\n", encoding="utf-8")

    print("2/5 Calculating KPIs...")
    k = a.kpis(sales, cancellations)
    (OUT / "kpis.json").write_text(json.dumps(k, indent=2), encoding="utf-8")

    print("3/5 Running analyses...")
    monthly = a.monthly_revenue(sales)
    countries = a.revenue_by_country(sales)
    products = a.top_products(sales)
    weekday_hour = a.orders_by_weekday_hour(sales)
    rfm = a.rfm(customers)
    segments = a.segment_summary(rfm)
    retention = a.cohort_retention(customers)
    rfm.to_csv(OUT / "rfm_customers.csv")
    segments.round(4).to_csv(OUT / "rfm_segment_summary.csv")
    monthly.round(4).to_csv(OUT / "monthly_revenue.csv")

    print("4/5 Running SQL queries...")
    sql = run_all(sales)
    md = ["# SQL query results\n", "Queries are in `sql/queries.sql`, run on the cleaned data in SQLite.\n"]
    for name, df in sql.items():
        md += [f"## {name.replace('_', ' ').capitalize()}\n", df.to_markdown(index=False, floatfmt=",.2f", intfmt=","), ""]
    (OUT / "sql_results.md").write_text("\n".join(md), encoding="utf-8")

    print("5/5 Drawing charts...")
    charts.monthly_revenue_chart(monthly, CHARTS)
    charts.countries_chart(countries, k["uk_revenue_share"], CHARTS)
    charts.products_chart(products, CHARTS)
    charts.segments_chart(segments, CHARTS)
    charts.heatmap_weekday_hour(weekday_hour, CHARTS)
    charts.cohort_chart(retention, CHARTS)

    print("\nKey figures")
    for key, value in k.items():
        print(f"  {key:<24} {value}")
    print(f"\nDone. See the {OUT.name}/ folder.")


if __name__ == "__main__":
    main()

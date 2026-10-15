"""
Data cleaning for the UCI Online Retail dataset.

Every cleaning rule is a separate, named step, and the number of rows each
step removes is recorded. This gives a data quality report that explains
exactly what happened to the data, which is what a stakeholder would ask for.
"""
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "online_retail.csv.gz"

# Stock codes that are not real products (postage, fees, manual adjustments, samples)
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "D", "C2", "S", "B", "PADS", "CRUK",
    "BANK CHARGES", "AMAZONFEE",
}

# Make country names consistent and readable
COUNTRY_FIXES = {"EIRE": "Ireland", "RSA": "South Africa", "European Community": "EU (unspecified)"}


def load_raw(path=DATA_PATH):
    """Load the raw transactions with the right data types."""
    df = pd.read_csv(
        path,
        dtype={"InvoiceNo": "string", "StockCode": "string", "Description": "string",
               "Country": "string"},
        parse_dates=["InvoiceDate"],
    )
    return df


def is_non_product(stock_codes):
    codes = stock_codes.str.upper().str.strip()
    return codes.isin(NON_PRODUCT_CODES) | codes.str.startswith("GIFT_")


def reversed_by_cancellation(sales, cancellations):
    """
    Flag sale lines that were later cancelled in full: same customer, same
    product, same quantity, and the cancellation happened on or after the sale.
    Without this, huge orders that were placed and then immediately cancelled
    (e.g. one order of 80,995 units) would distort the product rankings.
    """
    keys = ["CustomerID", "StockCode"]
    c = cancellations[keys + ["Quantity", "InvoiceDate"]].copy()
    c["Quantity"] = -c["Quantity"]
    c = c.rename(columns={"InvoiceDate": "CancelDate"}).dropna(subset=["CustomerID"])
    s = sales.reset_index()[["index"] + keys + ["Quantity", "InvoiceDate"]]
    matched = s.merge(c, on=keys + ["Quantity"])
    matched = matched[matched["CancelDate"] >= matched["InvoiceDate"]]
    # each cancellation reverses only its closest earlier sale
    matched = matched.sort_values("InvoiceDate").drop_duplicates(
        subset=keys + ["Quantity", "CancelDate"], keep="last")
    return sales.index.isin(matched["index"])


def clean(raw):
    """
    Clean the raw data. Returns (sales, cancellations, report).

    sales          -> valid product sales, one row per invoice line, with Revenue
    cancellations  -> cancelled invoice lines (kept separately for analysis)
    report         -> list of (step, rows_removed, rows_remaining)
    """
    df = raw.copy()
    report = [("Raw rows loaded", 0, len(df))]

    def step(name, mask_to_remove):
        nonlocal df
        removed = int(mask_to_remove.sum())
        df = df[~mask_to_remove]
        report.append((name, removed, len(df)))

    step("Exact duplicate rows", df.duplicated())

    is_cancel = df["InvoiceNo"].str.startswith("C")
    cancellations = df[is_cancel].copy()
    step("Cancelled invoices (InvoiceNo starts with 'C')", is_cancel)

    step("Zero or negative quantity (returns/adjustments)", df["Quantity"] <= 0)
    step("Sales reversed by an exact-match cancellation", reversed_by_cancellation(df, cancellations))
    step("Zero or negative unit price (free items, bad debt)", df["UnitPrice"] <= 0)
    step("Non-product codes (postage, fees, samples)", is_non_product(df["StockCode"]))

    df = df.copy()
    df["Description"] = df["Description"].str.replace(r"\s+", " ", regex=True).str.strip().str.upper()
    df["Country"] = df["Country"].replace(COUNTRY_FIXES)
    df["CustomerID"] = df["CustomerID"].astype("Int64")
    df["Revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M")

    return df.reset_index(drop=True), cancellations, report


def with_customers(sales):
    """Rows with a CustomerID (needed for customer-level analysis such as RFM)."""
    return sales[sales["CustomerID"].notna()].copy()


def quality_report_markdown(raw, report, sales):
    """Render the cleaning steps and remaining issues as a Markdown table."""
    lines = ["| Step | Rows removed | Rows remaining |", "|---|---:|---:|"]
    for name, removed, remaining in report:
        lines.append(f"| {name} | {removed:,} | {remaining:,} |")
    missing_cust = int(sales["CustomerID"].isna().sum())
    lines += [
        "",
        f"- Raw rows with a missing **CustomerID**: {int(raw['CustomerID'].isna().sum()):,} "
        f"({raw['CustomerID'].isna().mean():.1%}).",
        f"- Clean sales rows without a CustomerID: {missing_cust:,} ({missing_cust / len(sales):.1%}). "
        "These are kept for revenue and product analysis but excluded from customer analysis (RFM, cohorts).",
        f"- Raw rows with a missing **Description**: {int(raw['Description'].isna().sum()):,} "
        "(all removed by the steps above).",
    ]
    return "\n".join(lines)

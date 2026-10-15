"""
Run the SQL queries in sql/queries.sql against the cleaned data.

The cleaned sales DataFrame is loaded into an in-memory SQLite database,
so the same data can be analysed with both Pandas and SQL.
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "queries.sql"


def load_queries(path=SQL_FILE):
    """Split the .sql file into {name: query} using the '-- name:' markers."""
    text = Path(path).read_text(encoding="utf-8")
    parts = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.M)
    return {name: body.strip() for name, body in zip(parts[1::2], parts[2::2])}


def to_sqlite(sales):
    con = sqlite3.connect(":memory:")
    table = sales.copy()
    table["InvoiceMonth"] = table["InvoiceMonth"].astype(str)
    table["InvoiceDate"] = table["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    table["CustomerID"] = table["CustomerID"].astype("float")
    table.to_sql("sales", con, index=False)
    con.execute("CREATE INDEX idx_invoice ON sales(InvoiceNo)")
    return con


def run_all(sales):
    con = to_sqlite(sales)
    results = {name: pd.read_sql_query(q, con) for name, q in load_queries().items()}
    con.close()
    return results

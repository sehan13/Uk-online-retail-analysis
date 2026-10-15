"""
Tests for the cleaning rules, analysis functions and SQL queries, using a
small hand-made dataset so every expected number can be checked by eye.

Run with:   python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import analysis as a                               # noqa: E402
from clean import clean, with_customers            # noqa: E402
from sql_analysis import load_queries, run_all     # noqa: E402

COLS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


def make_raw(rows):
    df = pd.DataFrame(rows, columns=COLS)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    for c in ("InvoiceNo", "StockCode", "Description", "Country"):
        df[c] = df[c].astype("string")
    df["CustomerID"] = df["CustomerID"].astype("float")
    return df


RAW = make_raw([
    # good sales
    ["1001", "A1", "red  mug ", 2, "2011-01-05 10:00", 5.0, 1, "United Kingdom"],
    ["1001", "B1", "BLUE PLATE", 1, "2011-01-05 10:00", 10.0, 1, "United Kingdom"],
    ["1002", "A1", "RED MUG", 4, "2011-02-10 12:00", 5.0, 2, "EIRE"],
    ["1003", "B1", "BLUE PLATE", 3, "2011-02-11 09:00", 10.0, None, "France"],
    # exact duplicate of the first row
    ["1001", "A1", "red  mug ", 2, "2011-01-05 10:00", 5.0, 1, "United Kingdom"],
    # huge order later cancelled in full
    ["1004", "A1", "RED MUG", 500, "2011-03-01 09:00", 5.0, 2, "EIRE"],
    ["C2001", "A1", "RED MUG", -500, "2011-03-01 09:30", 5.0, 2, "EIRE"],
    # negative quantity without 'C' (adjustment)
    ["1005", "A1", "RED MUG", -1, "2011-03-02 09:00", 5.0, 1, "United Kingdom"],
    # free item
    ["1006", "B1", "BLUE PLATE", 1, "2011-03-03 09:00", 0.0, 1, "United Kingdom"],
    # postage line
    ["1007", "POST", "POSTAGE", 1, "2011-03-04 09:00", 18.0, 2, "EIRE"],
])


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.sales, self.cancellations, self.report = clean(RAW)

    def removed(self, step_start):
        return next(r[1] for r in self.report if r[0].startswith(step_start))

    def test_each_rule_removes_the_right_rows(self):
        self.assertEqual(self.removed("Exact duplicate"), 1)
        self.assertEqual(self.removed("Cancelled invoices"), 1)
        self.assertEqual(self.removed("Zero or negative quantity"), 1)
        self.assertEqual(self.removed("Sales reversed"), 1)
        self.assertEqual(self.removed("Zero or negative unit price"), 1)
        self.assertEqual(self.removed("Non-product codes"), 1)
        self.assertEqual(len(self.sales), 4)
        self.assertEqual(self.report[-1][2], 4)

    def test_cleaned_fields(self):
        s = self.sales
        self.assertEqual(s.loc[0, "Description"], "RED MUG")            # whitespace + case fixed
        self.assertIn("Ireland", set(s["Country"]))                      # EIRE renamed
        self.assertEqual(s["Revenue"].sum(), 10 + 10 + 20 + 30)
        self.assertEqual(len(self.cancellations), 1)

    def test_customer_rows_exclude_missing_ids(self):
        self.assertEqual(len(with_customers(self.sales)), 3)


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.sales, self.cancellations, _ = clean(RAW)

    def test_kpis(self):
        k = a.kpis(self.sales, self.cancellations)
        self.assertEqual(k["total_revenue"], 70.0)
        self.assertEqual(k["orders"], 3)
        self.assertEqual(k["customers"], 2)
        self.assertAlmostEqual(k["uk_revenue_share"], 20 / 70, places=4)

    def test_monthly_revenue(self):
        m = a.monthly_revenue(self.sales)
        self.assertEqual(m.loc[pd.Period("2011-01", "M"), "revenue"], 20)
        self.assertEqual(m.loc[pd.Period("2011-02", "M"), "revenue"], 50)

    def test_rfm_scores_and_segments(self):
        r = a.rfm(with_customers(self.sales))
        self.assertTrue(r[["R", "F", "M"]].isin(range(1, 6)).all().all())
        self.assertTrue(set(r["segment"]) <= {"Champions", "Loyal", "New / Promising", "At Risk",
                                               "Lost / Hibernating", "Needs Attention"})

    def test_cohort_month_zero_is_100_percent(self):
        r = a.cohort_retention(with_customers(self.sales))
        self.assertTrue((r[0] == 1.0).all())


class SqlTests(unittest.TestCase):
    def test_all_queries_load(self):
        self.assertEqual(len(load_queries()), 6)

    def test_sql_matches_pandas(self):
        sales, _, _ = clean(RAW)
        sql = run_all(sales)["monthly_revenue"].set_index("month")["revenue"]
        pandas_result = a.monthly_revenue(sales)["revenue"]
        for period, value in pandas_result.items():
            self.assertAlmostEqual(sql[str(period)], value, places=2)


if __name__ == "__main__":
    unittest.main()

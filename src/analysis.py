"""
Analysis functions: each answers one business question and returns a DataFrame.
"""
import pandas as pd

# The data ends on 9 Dec 2011, so December 2011 is only a partial month.
LAST_FULL_MONTH = pd.Period("2011-11", "M")


def kpis(sales, cancellations):
    full = sales[sales["InvoiceMonth"] <= LAST_FULL_MONTH]
    orders = sales.groupby("InvoiceNo")["Revenue"].sum()
    customers = sales[sales["CustomerID"].notna()]
    orders_per_customer = customers.groupby("CustomerID")["InvoiceNo"].nunique()
    uk_share = sales.loc[sales["Country"] == "United Kingdom", "Revenue"].sum() / sales["Revenue"].sum()
    n_cancelled = cancellations["InvoiceNo"].nunique()
    n_orders = sales["InvoiceNo"].nunique()
    return {
        "total_revenue": round(float(sales["Revenue"].sum()), 2),
        "revenue_dec10_to_nov11": round(float(full["Revenue"].sum()), 2),
        "orders": int(n_orders),
        "customers": int(customers["CustomerID"].nunique()),
        "products": int(sales["StockCode"].nunique()),
        "countries": int(sales["Country"].nunique()),
        "average_order_value": round(float(orders.mean()), 2),
        "uk_revenue_share": round(float(uk_share), 4),
        "repeat_customer_rate": round(float((orders_per_customer > 1).mean()), 4),
        "cancelled_invoice_rate": round(n_cancelled / (n_orders + n_cancelled), 4),
    }


def monthly_revenue(sales):
    m = (sales[sales["InvoiceMonth"] <= LAST_FULL_MONTH]
         .groupby("InvoiceMonth")
         .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"),
              customers=("CustomerID", "nunique")))
    m["avg_order_value"] = m["revenue"] / m["orders"]
    m["mom_growth"] = m["revenue"].pct_change()
    return m


def revenue_by_country(sales, top=10, exclude_uk=True):
    df = sales[sales["Country"] != "United Kingdom"] if exclude_uk else sales
    out = (df.groupby("Country")
             .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"),
                  customers=("CustomerID", "nunique")))
    out["avg_order_value"] = out["revenue"] / out["orders"]
    return out.sort_values("revenue", ascending=False).head(top)


def top_products(sales, top=10):
    return (sales.groupby("Description")
                 .agg(revenue=("Revenue", "sum"), units=("Quantity", "sum"),
                      orders=("InvoiceNo", "nunique"))
                 .sort_values("revenue", ascending=False).head(top))


def orders_by_weekday_hour(sales):
    orders = sales.drop_duplicates("InvoiceNo")
    table = pd.crosstab(orders["InvoiceDate"].dt.day_name(), orders["InvoiceDate"].dt.hour)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return table.reindex([d for d in order if d in table.index])


# ---------------------------------------------------------------- RFM segmentation
def rfm(customer_sales):
    """
    Recency, Frequency, Monetary value per customer, scored 1-5 by quintile,
    then grouped into named segments that a marketing team can act on.
    """
    snapshot = customer_sales["InvoiceDate"].max() + pd.Timedelta(days=1)
    r = customer_sales.groupby("CustomerID").agg(
        last_purchase=("InvoiceDate", "max"),
        frequency=("InvoiceNo", "nunique"),
        monetary=("Revenue", "sum"),
    )
    r["recency_days"] = (snapshot - r["last_purchase"]).dt.days

    # rank first so ties don't break the quintiles
    r["R"] = pd.qcut(r["recency_days"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    r["F"] = pd.qcut(r["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    r["M"] = pd.qcut(r["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    r["segment"] = r.apply(_segment, axis=1)
    return r.drop(columns="last_purchase")


def _segment(row):
    R, F = row["R"], row["F"]
    if R >= 4 and F >= 4:
        return "Champions"
    if R >= 3 and F >= 3:
        return "Loyal"
    if R >= 4:
        return "New / Promising"
    if R <= 2 and F >= 4:
        return "At Risk"
    if R <= 2 and F <= 2:
        return "Lost / Hibernating"
    return "Needs Attention"


def segment_summary(rfm_table):
    s = rfm_table.groupby("segment").agg(
        customers=("R", "size"), revenue=("monetary", "sum"),
        avg_recency_days=("recency_days", "mean"), avg_orders=("frequency", "mean"))
    s["customer_share"] = s["customers"] / s["customers"].sum()
    s["revenue_share"] = s["revenue"] / s["revenue"].sum()
    return s.sort_values("revenue", ascending=False)


# ---------------------------------------------------------------- cohort retention
def cohort_retention(customer_sales):
    """% of each monthly cohort (first purchase month) that bought again N months later."""
    df = customer_sales[customer_sales["InvoiceMonth"] <= LAST_FULL_MONTH][["CustomerID", "InvoiceMonth"]].drop_duplicates()
    first = df.groupby("CustomerID")["InvoiceMonth"].min().rename("cohort")
    df = df.join(first, on="CustomerID")
    df["months_since_first"] = (df["InvoiceMonth"] - df["cohort"]).apply(lambda d: d.n)
    counts = df.pivot_table(index="cohort", columns="months_since_first",
                            values="CustomerID", aggfunc="nunique")
    return counts.div(counts[0], axis=0)

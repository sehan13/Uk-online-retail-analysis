-- Business questions answered in SQL (SQLite).
-- Table: sales(InvoiceNo, StockCode, Description, Quantity, InvoiceDate,
--              UnitPrice, CustomerID, Country, Revenue, InvoiceMonth)
-- Each query starts with "-- name: <query_name>" so Python can run them by name.

-- name: monthly_revenue
-- Revenue, orders and average order value per month (Dec 2011 is a partial month).
SELECT InvoiceMonth                                  AS month,
       ROUND(SUM(Revenue), 2)                        AS revenue,
       COUNT(DISTINCT InvoiceNo)                     AS orders,
       ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM sales
WHERE InvoiceMonth <= '2011-11'
GROUP BY InvoiceMonth
ORDER BY InvoiceMonth;

-- name: top_international_markets
-- Best markets outside the UK, with customers and average order value.
SELECT Country,
       ROUND(SUM(Revenue), 0)                        AS revenue,
       COUNT(DISTINCT CustomerID)                    AS customers,
       ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 0) AS avg_order_value
FROM sales
WHERE Country <> 'United Kingdom'
GROUP BY Country
ORDER BY revenue DESC
LIMIT 10;

-- name: repeat_vs_one_off_customers
-- How much revenue comes from customers who ordered more than once?
WITH per_customer AS (
    SELECT CustomerID,
           COUNT(DISTINCT InvoiceNo) AS orders,
           SUM(Revenue)              AS revenue
    FROM sales
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
)
SELECT CASE WHEN orders > 1 THEN 'Repeat' ELSE 'One-off' END AS customer_type,
       COUNT(*)                                             AS customers,
       ROUND(SUM(revenue), 0)                               AS revenue,
       ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM per_customer), 1) AS pct_of_revenue
FROM per_customer
GROUP BY customer_type;

-- name: top_10_customers_share
-- Concentration risk: share of revenue from the top 10 customers.
WITH ranked AS (
    SELECT CustomerID, SUM(Revenue) AS revenue,
           RANK() OVER (ORDER BY SUM(Revenue) DESC) AS rnk
    FROM sales
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
)
SELECT ROUND(SUM(CASE WHEN rnk <= 10 THEN revenue END), 0)            AS top_10_revenue,
       ROUND(100.0 * SUM(CASE WHEN rnk <= 10 THEN revenue END) / SUM(revenue), 1) AS pct_of_customer_revenue
FROM ranked;

-- name: busiest_weekdays
-- Orders by day of week (SQLite strftime: 0 = Sunday).
SELECT CASE CAST(strftime('%w', InvoiceDate) AS INTEGER)
            WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
            ELSE 'Saturday' END                     AS weekday,
       COUNT(DISTINCT InvoiceNo)                    AS orders,
       ROUND(SUM(Revenue), 0)                       AS revenue
FROM sales
GROUP BY strftime('%w', InvoiceDate)
ORDER BY orders DESC;

-- name: products_bought_together
-- Product pairs that most often appear on the same invoice (basket analysis).
WITH lines AS (
    SELECT DISTINCT InvoiceNo, Description FROM sales
)
SELECT a.Description AS product_a,
       b.Description AS product_b,
       COUNT(*)      AS invoices_together
FROM lines a
JOIN lines b
  ON a.InvoiceNo = b.InvoiceNo
 AND a.Description < b.Description
GROUP BY a.Description, b.Description
ORDER BY invoices_together DESC
LIMIT 10;

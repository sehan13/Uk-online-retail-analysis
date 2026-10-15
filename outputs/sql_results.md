# SQL query results

Queries are in `sql/queries.sql`, run on the cleaned data in SQLite.

## Monthly revenue

| month   |      revenue |   orders |   avg_order_value |
|:--------|-------------:|---------:|------------------:|
| 2010-12 |   766,924.53 |    1,542 |            497.36 |
| 2011-01 |   564,732.93 |    1,073 |            526.31 |
| 2011-02 |   504,714.91 |    1,088 |            463.89 |
| 2011-03 |   682,306.56 |    1,431 |            476.80 |
| 2011-04 |   509,523.35 |    1,225 |            415.94 |
| 2011-05 |   732,652.39 |    1,652 |            443.49 |
| 2011-06 |   690,041.68 |    1,511 |            456.68 |
| 2011-07 |   682,545.01 |    1,445 |            472.35 |
| 2011-08 |   715,191.69 |    1,336 |            535.32 |
| 2011-09 | 1,017,641.99 |    1,807 |            563.17 |
| 2011-10 | 1,072,898.55 |    1,987 |            539.96 |
| 2011-11 | 1,439,152.18 |    2,740 |            525.24 |

## Top international markets

| Country     |    revenue |   customers |   avg_order_value |
|:------------|-----------:|------------:|------------------:|
| Netherlands | 283,444.00 |           9 |          3,048.00 |
| Ireland     | 261,663.00 |           3 |            938.00 |
| Germany     | 203,849.00 |          94 |            460.00 |
| France      | 182,835.00 |          87 |            481.00 |
| Australia   | 137,124.00 |           9 |          2,587.00 |
| Switzerland |  52,713.00 |          21 |          1,098.00 |
| Spain       |  52,030.00 |          29 |            598.00 |
| Japan       |  37,314.00 |           8 |          1,964.00 |
| Belgium     |  36,814.00 |          25 |            376.00 |
| Sweden      |  36,411.00 |           8 |          1,103.00 |

## Repeat vs one off customers

| customer_type   |   customers |      revenue |   pct_of_revenue |
|:----------------|------------:|-------------:|-----------------:|
| One-off         |       1,502 |   540,870.00 |             6.50 |
| Repeat          |       2,822 | 7,772,597.00 |            93.50 |

## Top 10 customers share

|   top_10_revenue |   pct_of_customer_revenue |
|-----------------:|--------------------------:|
|     1,375,585.00 |                     16.50 |

## Busiest weekdays

| weekday   |   orders |      revenue |
|:----------|---------:|-------------:|
| Thursday  |    4,185 | 2,100,009.00 |
| Wednesday |    3,646 | 1,764,575.00 |
| Tuesday   |    3,485 | 1,970,337.00 |
| Friday    |    3,086 | 1,533,947.00 |
| Monday    |    3,051 | 1,663,783.00 |
| Sunday    |    2,195 |   790,807.00 |

## Products bought together

| product_a                       | product_b                         |   invoices_together |
|:--------------------------------|:----------------------------------|--------------------:|
| JUMBO BAG PINK POLKADOT         | JUMBO BAG RED RETROSPOT           |                 817 |
| GREEN REGENCY TEACUP AND SAUCER | ROSES REGENCY TEACUP AND SAUCER   |                 760 |
| JUMBO BAG RED RETROSPOT         | JUMBO STORAGE BAG SUKI            |                 718 |
| JUMBO BAG RED RETROSPOT         | JUMBO SHOPPER VINTAGE RED PAISLEY |                 676 |
| LUNCH BAG RED RETROSPOT         | LUNCH BAG SUKI DESIGN             |                 652 |
| LUNCH BAG BLACK SKULL.          | LUNCH BAG RED RETROSPOT           |                 637 |
| ALARM CLOCK BAKELIKE GREEN      | ALARM CLOCK BAKELIKE RED          |                 636 |
| GREEN REGENCY TEACUP AND SAUCER | PINK REGENCY TEACUP AND SAUCER    |                 626 |
| LUNCH BAG PINK POLKADOT         | LUNCH BAG RED RETROSPOT           |                 603 |
| PINK REGENCY TEACUP AND SAUCER  | ROSES REGENCY TEACUP AND SAUCER   |                 590 |

# Data quality report

| Step | Rows removed | Rows remaining |
|---|---:|---:|
| Raw rows loaded | 0 | 541,909 |
| Exact duplicate rows | 5,268 | 536,641 |
| Cancelled invoices (InvoiceNo starts with 'C') | 9,251 | 527,390 |
| Zero or negative quantity (returns/adjustments) | 1,336 | 526,054 |
| Sales reversed by an exact-match cancellation | 2,860 | 523,194 |
| Zero or negative unit price (free items, bad debt) | 1,176 | 522,018 |
| Non-product codes (postage, fees, samples) | 2,286 | 519,732 |

- Raw rows with a missing **CustomerID**: 135,080 (24.9%).
- Clean sales rows without a CustomerID: 131,387 (25.3%). These are kept for revenue and product analysis but excluded from customer analysis (RFM, cohorts).
- Raw rows with a missing **Description**: 1,454 (all removed by the steps above).

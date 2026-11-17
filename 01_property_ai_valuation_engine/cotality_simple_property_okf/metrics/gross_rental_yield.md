---
type: "Metric"
title: "Gross Rental Yield"
description: "Annualized gross monthly rent divided by sold price on move-in-ready residential properties, excluding major fixer-uppers."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_simple/metrics/gross_rental_yield"
tags: ["cotality", "kpi", "rental-yield"]
status: "stable"
stale_after: "2027-12-31T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T21:45:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T21:46:00Z"
sources:
  - id: "analytics-guide"
    resource: "https://github.com/GoogleCloudPlatform/open-knowledge-format"
    title: "Cotality Residential Valuation & Yield Guide"
    author: "human:cotality_analytics_team"
    last_modified: "2026-10-30T21:45:00Z"
---

# Gross Rental Yield (%)

Measures annualized rental return across [Property Comps](../tables/property_comps.md) and [Properties](../tables/properties.md) [^analytics-guide]:

* **Formula**: `ROUND(100.0 * (12.0 * monthly_rent_usd) / NULLIF(sold_price_usd, 0), 2)`
* **Standard Governance Rule**: Exclude properties requiring major structural/roof rehabilitation (`is_fixer_upper = FALSE` / `is_move_in_ready = TRUE`) and deduct a `5%` annual vacancy allowance (`0.95` effective collection factor) when reporting **Effective Gross Rental Yield** to investors.
* **Attested SQL**: See [Gross Rental Yield SQL](../computations/gross_rental_yield_sql.md).

---
type: "Attested Computation"
title: "Gross Rental Yield SQL"
description: "Verified BigQuery GoogleSQL query computing Effective Gross Rental Yield (%) by metro_area."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property/computations/gross_rental_yield_sql"
runtime: "bigquery"
tags: ["cotality", "attested-sql", "yield"]
status: "stable"
stale_after: "2027-12-31T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T21:45:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T21:46:00Z"
sources:
  - id: "yield-spec"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property/metrics/gross_rental_yield"
    title: "Gross Rental Yield Metric Definition"
    author: "human:cotality_analytics_team"
    last_modified: "2026-10-30T21:45:00Z"
---

# Gross Rental Yield SQL

Implements [Gross Rental Yield](../metrics/gross_rental_yield.md) across [Property Comps](../tables/property_comps.md) [^yield-spec].

## Computation

```sql
SELECT
  metro_area,
  COUNT(*) AS move_in_ready_comps,
  ROUND(AVG(sold_price_usd), 0) AS avg_sold_price_usd,
  ROUND(AVG(monthly_rent_usd), 0) AS avg_monthly_rent_usd,
  ROUND(
    100.0 * SAFE_DIVIDE(SUM(12.0 * monthly_rent_usd * 0.95), SUM(sold_price_usd)),
    2
  ) AS effective_gross_rental_yield_pct
FROM `${PROJECT_ID}.cotality_property.property_comps`
WHERE is_fixer_upper = FALSE
GROUP BY metro_area
ORDER BY effective_gross_rental_yield_pct DESC;
```

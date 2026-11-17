---
type: "Attested Computation"
title: "Gross Rental Yield SQL"
description: "Verified BigQuery GoogleSQL query computing Effective Gross Rental Yield (%) by metro_area."
resource: "//bigquery.googleapis.com/projects/cotality-proj/datasets/cotality_property/computations/gross_rental_yield_sql"
runtime: "bigquery"
---

# Gross Rental Yield SQL

Implements [Gross Rental Yield](../metrics/effective_gross_rental_yield.md) across [Property Comps](../tables/property_comps.md).

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
FROM `cotality-proj.cotality_property.property_comps`
WHERE is_fixer_upper = FALSE
GROUP BY metro_area
ORDER BY effective_gross_rental_yield_pct DESC;
```

---
type: "Metric"
title: "Gross Rental Yield"
description: "Effective annualized rental yield (%) on move-in-ready residential homes after a 5% vacancy allowance."
resource: "//bigquery.googleapis.com/projects/cotality-proj/datasets/cotality_property/metrics/gross_rental_yield"
---

# Effective Gross Rental Yield (%)

* **Formula**: `ROUND(100.0 * SAFE_DIVIDE(SUM(12.0 * monthly_rent_usd * 0.95), SUM(sold_price_usd)), 2)`
* **Governance Rule**: Include only move-in-ready residential homes (`is_fixer_upper = FALSE`) and apply a `0.95` effective collection factor (`5%` annual vacancy allowance).
* **Attested SQL**: See [Gross Rental Yield SQL](../computations/effective_gross_rental_yield_sql.md).

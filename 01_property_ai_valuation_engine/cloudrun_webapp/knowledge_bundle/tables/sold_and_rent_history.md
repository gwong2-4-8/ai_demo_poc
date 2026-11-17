---
type: "BigQuery Table"
title: "Sold and Rent History"
description: "Monthly historical median_sold_price_usd and avg_monthly_rent_usd across 5 US metros."
resource: "//bigquery.googleapis.com/projects/cotality-proj/datasets/cotality_property/tables/sold_and_rent_history"
---

# Sold and Rent History (`cotality-proj.cotality_property.sold_and_rent_history`)

Partitioned by `month_date` and clustered by `metro_area` (`month_date`, `metro_area`, `median_sold_price_usd`, `avg_monthly_rent_usd`, `homes_sold_count`) for zero-shot `AI.FORECAST` projections.

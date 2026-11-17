---
type: "BigQuery Table"
title: "Sold and Rent History"
description: "Monthly historical median sold price and average monthly rent across 5 US metros (72 months per metro) for AI.FORECAST."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property/tables/sold_and_rent_history"
tags: ["cotality", "sold-history", "rent-history", "timesfm"]
status: "stable"
stale_after: "2027-12-31T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T21:45:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T21:46:00Z"
sources:
  - id: "hist-cols"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property/INFORMATION_SCHEMA.COLUMNS"
    title: "INFORMATION_SCHEMA.COLUMNS for sold_and_rent_history"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T21:45:00Z"
---

# Sold and Rent History (`sold_and_rent_history`)

Partitioned by `month_date` and clustered by `metro_area`, storing 72 monthly observations (`2020-01-01` to `2025-12-01`) of `median_sold_price_usd`, `avg_monthly_rent_usd`, and `homes_sold_count` for zero-shot `AI.FORECAST` projections [^hist-cols].

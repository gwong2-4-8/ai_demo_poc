---
type: "BigQuery Table"
title: "Regional Rent History"
description: "Monthly historical market rent index across 6 US metros and property types (84 months per series) for TimesFM forecasting."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/tables/regional_rent_history"
tags: ["cotality", "time-series", "rent-growth", "timesfm"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "rent-hist-ddl"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/INFORMATION_SCHEMA.COLUMNS"
    title: "BigQuery INFORMATION_SCHEMA Columns for regional_rent_history"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T04:00:00Z"
---

# Regional Rent History (`regional_rent_history`)

Provides 84 monthly observations (`2019-01-01` through `2025-12-01`) per `(metro_area, property_type)` series for zero-shot forecasting with `AI.FORECAST` [^rent-hist-ddl].

## Schema

| Column | Type | Business Definition |
| :--- | :--- | :--- |
| `month_date` | `DATE` | First calendar day of the observation month (`PARTITION BY month_date`). |
| `metro_area` | `STRING` | Metropolitan market identifier (`CLUSTER BY metro_area, property_type`). |
| `property_type` | `STRING` | Asset class (`Single-Family`, `Townhome`). |
| `avg_monthly_rent_usd` | `FLOAT64` | Seasonally observed average signed lease rent in USD. |
| `occupancy_rate` | `FLOAT64` | Market-level physical occupancy ratio (`0.0` to `1.0`). |

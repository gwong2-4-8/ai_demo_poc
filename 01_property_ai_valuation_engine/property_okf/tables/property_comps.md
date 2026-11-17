---
type: "BigQuery Table"
title: "Property Comps"
description: "Comparable sold and leased residential properties with verified sold_price_usd and monthly_rent_usd labels for AI.PREDICT."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property/tables/property_comps"
tags: ["cotality", "comps", "valuation", "tabfm"]
status: "stable"
stale_after: "2027-12-31T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T21:45:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T21:46:00Z"
sources:
  - id: "comps-cols"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property/INFORMATION_SCHEMA.COLUMNS"
    title: "INFORMATION_SCHEMA.COLUMNS for property_comps"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T21:45:00Z"
---

# Property Comps (`property_comps`)

Contains 240 comparable closed sales and leases (`TRAIN` and `VALIDATION` splits) matching the feature columns of [Properties](properties.md), powering zero-shot `AI.PREDICT` estimates of `sold_price_usd` and `monthly_rent_usd` [^comps-cols].

---
type: "BigQuery Table"
title: "Property Valuation Comps"
description: "Verified comparable lease transactions and renewal outcomes used as tabular foundation model context for AI.PREDICT."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/tables/property_valuation_comps"
tags: ["cotality", "valuation", "comps", "tabfm"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "comps-ddl"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/INFORMATION_SCHEMA.COLUMNS"
    title: "BigQuery INFORMATION_SCHEMA Columns for property_valuation_comps"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T04:00:00Z"
---

# Property Valuation Comps (`property_valuation_comps`)

Contains 360 verified comparable residential leases (`TRAIN` and `VALIDATION` splits) with identical physical, neighborhood, and hazard attributes as [Properties Master Table](properties.md), enabling zero-shot `AI.PREDICT` regression (`market_monthly_rent_usd`) and classification (`lease_renewal_outcome`) without `CREATE MODEL` training pipelines [^comps-ddl].

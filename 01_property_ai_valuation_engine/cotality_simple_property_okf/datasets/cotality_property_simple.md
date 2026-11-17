---
type: "BigQuery Dataset"
title: "Cotality Simple Property Dataset"
description: "Streamlined 3-table BigQuery dataset for residential property photo inspection, sold/rent forecasting, and comparable home valuation."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_simple"
tags: ["cotality", "real-estate", "bigquery", "multimodal"]
status: "stable"
stale_after: "2027-12-31T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T21:45:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T21:46:00Z"
sources:
  - id: "bq-schemata"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_simple/INFORMATION_SCHEMA.SCHEMATA"
    title: "BigQuery Dataset Metadata"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T21:45:00Z"
---

# Cotality Simple Property Dataset

Unifies [Properties](../tables/properties.md), [Sold and Rent History](../tables/sold_and_rent_history.md), and [Property Comps](../tables/property_comps.md) in BigQuery [^bq-schemata].

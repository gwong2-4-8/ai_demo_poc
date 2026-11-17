---
type: "BigQuery Dataset"
title: "Cotality Property AI Dataset"
description: "Primary BigQuery dataset unifying parcel structural records, tenant maintenance logs, metro rent time series, comparable leases, and Cloud Storage multimodal inspection references."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai"
tags: ["cotality", "property-management", "bigquery", "multimodal"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "bq-info-schema"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/INFORMATION_SCHEMA.SCHEMATA"
    title: "BigQuery Dataset Metadata Catalog"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T04:00:00Z"
---

# Cotality Property AI Dataset

The `cotality_property_ai` dataset serves as the single analytical and operational foundation for Cotality property portfolio management in the `US` multi-region [^bq-info-schema].

## Core Tables

* [Properties Master Table](../tables/properties.md) — Active residential and small-multifamily parcels linked to Cloud Storage exterior/roof inspection imagery.
* [Maintenance Requests](../tables/maintenance_requests.md) — Unstructured tenant and inspector work-order descriptions triaged with `AI.IF` and `AI.CLASSIFY`.
* [Regional Rent History](../tables/regional_rent_history.md) — 84-month historical rent roll index across 6 US metros used by `AI.FORECAST`.
* [Property Valuation Comps](../tables/property_valuation_comps.md) — Hedonic comparable leases used as reference examples for `AI.PREDICT`.

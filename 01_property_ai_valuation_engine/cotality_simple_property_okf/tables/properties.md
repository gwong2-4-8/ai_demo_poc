---
type: "BigQuery Table"
title: "Properties"
description: "One row per residential property with bedrooms, bathrooms, square footage, listing notes, and a Cloud Storage exterior photo URI."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_simple/tables/properties"
tags: ["cotality", "properties", "objectref"]
status: "stable"
stale_after: "2027-12-31T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T21:45:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T21:46:00Z"
sources:
  - id: "prop-cols"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_simple/INFORMATION_SCHEMA.COLUMNS"
    title: "INFORMATION_SCHEMA.COLUMNS for properties"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T21:45:00Z"
---

# Properties (`properties`)

Active residential portfolio table (`CLUSTER BY metro_area, property_type`) linked to real property photos in Cloud Storage via `gcs_image_uri` and `OBJ.MAKE_REF` [^prop-cols].

## Schema

| Column | Type | Definition |
| :--- | :--- | :--- |
| `property_id` | `STRING` | Unique property identifier (`PROP-101`..). |
| `address` | `STRING` | Street address and metro market. |
| `metro_area` | `STRING` | Metro market (`Austin, TX`, `Miami, FL`, `Denver, CO`, `Phoenix, AZ`, `Seattle, WA`). |
| `property_type` | `STRING` | Residential home type (`Single-Family`, `Townhome`, `Cottage`). |
| `sqft` | `INT64` | Interior living area in square feet. |
| `bedrooms` | `INT64` | Bedroom count. |
| `bathrooms` | `FLOAT64` | Bathroom count. |
| `year_built` | `INT64` | Construction year. |
| `has_pool_or_view` | `BOOL` | Indicates pool, water view, or premium outdoor amenity. |
| `list_price_usd` | `FLOAT64` | Current asking or estimated basis price in USD. |
| `current_monthly_rent_usd` | `FLOAT64` | Current in-place or target monthly rent in USD. |
| `listing_notes` | `STRING` | Plain-English agent/inspector property description evaluated by `AI.IF` and `AI.CLASSIFY`. |
| `gcs_image_uri` | `STRING` | Cloud Storage URI (`gs://.../images/*.jpg`) of the property exterior photograph. |

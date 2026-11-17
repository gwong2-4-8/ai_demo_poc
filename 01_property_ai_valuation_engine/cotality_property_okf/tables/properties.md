---
type: "BigQuery Table"
title: "Properties Master Table"
description: "One row per managed property parcel with physical characteristics, hazard risk scores, current monthly lease rent, operating expenses, and Cloud Storage inspection image URI."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/tables/properties"
tags: ["cotality", "parcel", "underwriting", "objectref"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "properties-ddl"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/INFORMATION_SCHEMA.COLUMNS"
    title: "BigQuery INFORMATION_SCHEMA Columns for properties"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T04:00:00Z"
---

# Properties Master Table (`properties`)

Stores parcel-level structural attributes, peril risk classifications, financial lease terms, and unstructured Cloud Storage image pointers (`gcs_image_uri`) converted via `OBJ.MAKE_REF` during multimodal underwriting [^properties-ddl].

## Storage Layout

* **Clustering**: `CLUSTER BY metro_area, property_type, risk_zone` to accelerate regional portfolio filtering and `AI.PREDICT` comparable joins.

## Schema

| Column | Type | Business Definition |
| :--- | :--- | :--- |
| `property_id` | `STRING` | Primary property identifier (`PROP-1001`..`PROP-1180`). |
| `apn_parcel_id` | `STRING` | Assessor Parcel Number (APN) tax record key. |
| `address` | `STRING` | Street address and metro state code. |
| `metro_area` | `STRING` | Metropolitan statistical market (`Austin, TX`, `Miami, FL`, `Denver, CO`, `Phoenix, AZ`, `Seattle, WA`, `Tampa, FL`). |
| `property_type` | `STRING` | Asset class (`Single-Family`, `Townhome`, `Small Multifamily`). |
| `year_built` | `INT64` | Original construction year. |
| `property_age_years` | `INT64` | Effective structural age in years (`2026 - year_built`). |
| `sqft` | `INT64` | Gross livable interior square footage. |
| `bedrooms` | `INT64` | Total bedroom count. |
| `bathrooms` | `FLOAT64` | Total full and half bathroom count. |
| `roof_material` | `STRING` | Primary roof covering (`Architectural Shingle`, `Clay Tile`, `Standing Seam Metal`, `Three-Tab Asphalt`). |
| `roof_age_years` | `INT64` | Years since last permitted roof replacement. |
| `risk_zone` | `STRING` | Natural hazard exposure tier (`Low`, `Moderate-Hail`, `High-Wind-Flood`, `Moderate-Wildfire`). |
| `hazard_risk_score` | `FLOAT64` | Composite Cotality peril vulnerability score (`0.0` to `1.0`). |
| `walkability_score` | `INT64` | Neighborhood amenity and transit accessibility score (`0` to `100`). |
| `has_solar_upgrade` | `BOOL` | Indicates permitted rooftop solar or high-efficiency heat-pump package. |
| `occupancy_status` | `STRING` | Lease occupancy state (`Occupied`, `Notice-Given`, `Vacant-Turn`). |
| `current_monthly_rent_usd` | `FLOAT64` | Contracted monthly base rent in USD (excludes pet/parking ancillary fees). |
| `annual_operating_expense_usd` | `FLOAT64` | Trailing 12-month property tax, insurance, HOA, and routine maintenance spend in USD. |
| `estimated_asset_value_usd` | `FLOAT64` | Current automated valuation model (AVM) asset basis in USD. |
| `prior_maintenance_claims_12m` | `INT64` | Count of reactive work orders logged in the trailing 12 months. |
| `gcs_image_uri` | `STRING` | Cloud Storage URI (`gs://.../images/*.png`) for exterior/roof inspection imagery. |

## Joins & Downstream Usage

* Joins to [Maintenance Requests](maintenance_requests.md) on `property_id`.
* Joins to [Regional Rent History](regional_rent_history.md) on `(metro_area, property_type)`.
* Supplies governed inputs to [Net Effective Rent Yield](../metrics/net_effective_rent_yield.md).

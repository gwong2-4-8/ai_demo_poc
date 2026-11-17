---
type: "BigQuery Table"
title: "Maintenance Requests"
description: "Tenant and inspector maintenance work orders partitioned by request_date and clustered by property_id and status."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/tables/maintenance_requests"
tags: ["cotality", "work-orders", "unstructured-text", "triage"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "maint-ddl"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/INFORMATION_SCHEMA.COLUMNS"
    title: "BigQuery INFORMATION_SCHEMA Columns for maintenance_requests"
    author: "process:bigquery_information_schema"
    last_modified: "2026-10-30T04:00:00Z"
---

# Maintenance Requests (`maintenance_requests`)

Captures raw natural-language maintenance tickets submitted via resident portals, SMS, and field inspection notes [^maint-ddl].

## Storage Layout

* **Partitioning**: `PARTITION BY request_date` (daily date partitioning for rolling SLA audits).
* **Clustering**: `CLUSTER BY property_id, status`.

## Schema

| Column | Type | Business Definition |
| :--- | :--- | :--- |
| `request_id` | `STRING` | Unique work-order ticket identifier (`REQ-5001`..). |
| `property_id` | `STRING` | Foreign key to [Properties Master Table](properties.md). |
| `request_date` | `DATE` | Date the ticket was submitted. |
| `reported_channel` | `STRING` | Intake channel (`Resident Portal`, `Inspector Mobile App`, `After-Hours Hotline`). |
| `status` | `STRING` | Ticket workflow state (`OPEN`, `IN_PROGRESS`, `RESOLVED`). |
| `tenant_description` | `STRING` | Free-text problem narrative evaluated by `AI.IF` and `AI.CLASSIFY`. |

---
type: "Metric"
title: "Severe Hazard Exposure Rate"
description: "Percentage of managed properties exhibiting either urgent visual roof/structural damage or an open 24-hour emergency maintenance ticket."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/metrics/severe_hazard_exposure_rate"
tags: ["cotality", "kpi", "hazard", "risk"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "risk-charter"
    resource: "https://github.com/GoogleCloudPlatform/open-knowledge-format"
    title: "Cotality Hazard Underwriting Standards"
    author: "human:cotality_risk_committee"
    last_modified: "2026-10-30T04:00:00Z"
---

# Severe Hazard Exposure Rate

Measures the proportion of properties in [Properties Master Table](../tables/properties.md) flagged by `AI.GENERATE` multimodal roof inspection (`urgent_remediation = TRUE`) or `AI.IF` emergency work-order triage (`is_emergency_dispatch = TRUE` on [Maintenance Requests](../tables/maintenance_requests.md)) [^risk-charter].

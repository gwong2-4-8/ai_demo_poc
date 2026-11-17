---
type: "Policy"
title: "Property Underwriting & Renewal Guardrail Policy"
description: "Mandatory operational guardrails for 24-hour emergency maintenance dispatch, roof hazard capital reserves, and renewal rent increase caps."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/policies/property_underwriting_policy"
tags: ["cotality", "policy", "compliance", "underwriting"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "ops-manual"
    resource: "https://github.com/GoogleCloudPlatform/open-knowledge-format"
    title: "Cotality Property Operations Governance Manual v2026.2"
    author: "human:cotality_risk_committee"
    last_modified: "2026-10-30T04:00:00Z"
---

# Property Underwriting & Renewal Guardrail Policy

Applies across all analytics, AI recommendations, and automated pricing actions on [Properties Master Table](../tables/properties.md) and [Maintenance Requests](../tables/maintenance_requests.md) [^ops-manual]:

1. **Safety & Habitability First (Freeze Rent Increases During Urgent Remediation)**: Any property with `urgent_remediation = TRUE` from exterior/roof imagery or an `OPEN` emergency ticket (`AI.IF` emergency dispatch) MUST have renewal rent increases capped at `0%` until remediation is verified complete.
2. **24-Hour Emergency Dispatch SLA**: Any work order involving active roof/plumbing water intrusion, exposed electrical wiring, gas odor, or HVAC failure in extreme weather MUST be dispatched within 24 hours.
3. **Renewal Adjustment Guardrail**: For stabilized properties free of urgent hazards where `AI.PREDICT` fair-market rent exceeds `current_monthly_rent_usd` by more than `8%`, cap single-cycle renewal offers at `+8%` to preserve tenant retention while capturing mark-to-market upside.
